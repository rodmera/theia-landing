"""Suite del sitio theia.cl — mobile-first (viewport default = iPhone 390×844).

Cubre lo que Rodrigo no va a revisar a mano:
  1. Smoke: todas las páginas cargan, un h1, title, sin errores JS reales.
  2. Overflow horizontal en móvil (el bug #1 de mobile).
  3. CTAs críticos del index (número BLOQUEADO por decisión, agendar, brochure).
  4. Regresión de registro: jerga prohibida fuera del texto visible.
  5. Consistencia comercial: precio único, demo 30 min (no 15).
  6. Sticky de WhatsApp visible en móvil.
  7. Screenshots móviles como evidencia (artifacts en CI).
"""
import json
import re
from pathlib import Path

import pytest

from conftest import BASE, PAGES, filtered_js_errors

SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)

# Regla de registro (CLAUDE.md §Registro y tono): jerga que NO puede aparecer
# en texto visible. "escalar a/al/a un humano|persona|equipo" SÍ se permite.
JERGA = [r"\bunicornios?\b", r"\bserie [ab]\b", r"levantar capital",
         r"\bSaaS\b", r"nivel enterprise", r"\bstack\b", r"cloud.native"]
ESCALAR_PROHIBIDO = re.compile(r"\bescalar\b(?! (a|al) (un |una |tu )?(humano|persona|equipo|agente))", re.I)


def visible_text(page):
    return page.evaluate("() => document.body.innerText")


def goto(page, path):
    resp = page.goto(BASE + path, wait_until="domcontentloaded")
    page.wait_for_timeout(400)  # animaciones de entrada / cc-init
    return resp


# ───────────────────────── 1. SMOKE (todas las páginas, MÓVIL) ─────────────────────────

@pytest.mark.parametrize("path", PAGES)
def test_smoke_mobile(mobile_page, path):
    resp = goto(mobile_page, path)
    assert resp and resp.ok, f"{path} devolvió {resp and resp.status}"
    assert mobile_page.title().strip(), f"{path} sin <title>"
    h1s = mobile_page.locator("h1").count()
    assert h1s == 1, f"{path} tiene {h1s} <h1> (debe ser 1)"
    errs = filtered_js_errors(mobile_page)
    assert not errs, f"{path} con errores JS reales: {errs[:2]}"


# ─────────────────── 2. OVERFLOW HORIZONTAL EN MÓVIL (el bug #1) ───────────────────

@pytest.mark.parametrize("path", PAGES)
def test_no_horizontal_overflow_mobile(mobile_page, path):
    """Lo que importa al usuario: ¿la página SE PUEDE scrollear de lado en el teléfono?
    (scrollWidth teórico da falsos positivos con menús off-canvas clippeados por
    overflow-x hidden — se intenta scrollear de verdad y se mide scrollX)."""
    goto(mobile_page, path)
    scroll_x = mobile_page.evaluate(
        "() => { window.scrollTo(120, 0); return window.scrollX || document.documentElement.scrollLeft; }")
    assert scroll_x <= 1, (
        f"{path} permite scroll horizontal real ({scroll_x}px) en 390px — hay contenido desbordado sin clippear")


# ───────────────────────── 3. CTAs CRÍTICOS DEL INDEX ─────────────────────────

def test_ctas_criticos_index(mobile_page):
    goto(mobile_page, "/")
    html = mobile_page.content()
    # Número BLOQUEADO por decisión de Rodrigo (2026-07-18): el US +1 206. No cambiarlo.
    assert "wa.me/12063858350" in html, "CTA WhatsApp roto o número cambiado (decisión cerrada: es el +1 206)"
    assert "calendar.app.google" in html, "link de agendar demo roto"
    # los 3 botones del hero visibles en móvil
    # Brochure fuera del hero por decisión (2026-07-19): el sitio es el brochure;
    # el PDF queda solo como asset del bot en conversación (y el archivo vive en el
    # repo para no romper links antiguos).
    for texto in ["Probar conversación en vivo", "Agenda una demo"]:
        assert mobile_page.get_by_text(texto).first.is_visible(), f"CTA '{texto}' no visible en móvil"


def test_home_no_promete_casos_ni_comparaciones_de_precio():
    """La home usa dogfooding como prueba hasta contar con permisos de casos reales."""
    html = (Path(__file__).parent.parent / "index.html").read_text(encoding="utf-8")
    assert "Usamos TheIA para" in html
    assert "atenderte." in html
    assert "inversionistas que alimentar" not in html
    assert "Ver casos extendidos" not in html


def test_funciones_organiza_la_ayuda_en_tres_resultados(mobile_page):
    """La página explica atención PYME sin exhibir catálogo técnico no disponible."""
    goto(mobile_page, "/funciones.html")
    text = visible_text(mobile_page)
    for texto in ["Atiende y orienta.", "Cotiza, agenda y hace seguimiento.",
                  "Tu equipo conserva el control.", "Probar conversación en vivo", "Agenda una demo"]:
        assert texto in text, f"funciones no explica: {texto}"
    for texto in ["Facebook Messenger", "Para desarrolladores", "Lead Scoring Inteligente"]:
        assert texto not in text, f"funciones volvió a exhibir capacidad no comunicable: {texto}"
    for texto in ["Atiende y orienta.", "Cotiza, agenda y hace seguimiento.",
                  "Tu equipo conserva el control."]:
        heading = mobile_page.get_by_text(texto, exact=True)
        heading.scroll_into_view_if_needed()
        mobile_page.wait_for_timeout(150)
        assert heading.evaluate("el => getComputedStyle(el).opacity") == "1", (
            f"{texto} queda oculto al llegar con scroll")
    html = (Path(__file__).parent.parent / "funciones.html").read_text(encoding="utf-8")
    for texto in ["Facebook Messenger", "Lead Scoring Inteligente", "Agent API", "OpenClaw"]:
        assert texto not in html, f"funciones conserva una promesa no comunicable en HTML público: {texto}"
    root = Path(__file__).parent.parent
    assert (root / "webchat-cta.js").is_file(), "falta el helper compartido de CTA WebChat"
    assert 'src="/webchat-cta.js"' in html


def test_casos_usa_dogfooding_sin_prueba_social_no_autorizada(mobile_page):
    """Hasta contar con permisos, casos ofrece una prueba real y no testimonios anónimos."""
    goto(mobile_page, "/casos.html")
    text = visible_text(mobile_page)
    assert "Mira cómo atendemos antes de decidir." in text
    assert "Te atendemos con TheIA" in text
    assert "Cliente en conversación" not in text
    assert "Métricas en preparación" not in text
    html = (Path(__file__).parent.parent / "casos.html").read_text(encoding="utf-8")
    assert 'src="/webchat-cta.js"' in html


def test_atencion_cliente_es_hub_del_paraguas(mobile_page):
    """HU-WEB-017: la página articula las 4 piezas (Atención, Pulse, CRM, Plataforma),
    lleva el claim A del paraguas y la sección de cumplimiento."""
    goto(mobile_page, "/atencion-cliente.html")
    text = visible_text(mobile_page)
    # Claim A — bajada reconocible
    assert "WhatsApp, Instagram y tu web" in text, "atencion-cliente no exhibe el claim A"
    assert "agenda de clientes" in text, "atencion-cliente perdió el lenguaje del dueño del claim A"
    # Las 4 piezas del paraguas mencionadas como cards/secciones
    for pieza in ["Atención", "TheIA Pulse", "CRM", "Plataforma"]:
        assert pieza in text, f"atencion-cliente no menciona la pieza {pieza}"
    # Honestidad — bloque "para quién no"
    assert "TheIA no es para ti" in text, "atencion-cliente omitió el bloque 'para quién no'"
    # Cumplimiento / Seguridad
    assert "Seguridad" in text or "Privacidad" in text, "atencion-cliente no menciona la sección de seguridad/privacidad"


def test_criterios_sin_nombres_en_copy_visible(mobile_page):
    """HU-WEB-013: la página enumera criterios sin nombrar plataformas competidoras.
    Los datos de precio están externalizados en JSON (no hardcoded en HTML)."""
    goto(mobile_page, "/criterios.html")
    text = visible_text(mobile_page)
    # Criterios clave mencionados
    for criterio in ["Modelo de cobro", "Compromiso mínimo", "Seguridad y privacidad",
                     "WhatsApp Business", "Por negocio"]:
        assert criterio in text, f"criterios no menciona: {criterio}"
    # Bloque honestidad ("TheIA NO")
    assert "TheIA NO" in text or "no hace" in text.lower(), (
        "criterios omitió el bloque de honestidad sobre lo que TheIA NO hace")
    # NO nombres de competidores en copy visible
    html = (Path(__file__).parent.parent / "criterios.html").read_text(encoding="utf-8")
    for nombre in ["Kommo", "Vambe", "Dapta", "Botpress"]:
        assert nombre not in html, (
            f"criterios.html nombra a {nombre} en copy visible (decisión 2026-07-29: sin nombres)")
    # Calculadora: archivo de datos presente y cargable
    data_file = Path(__file__).parent.parent / "data" / "criterios-precios.json"
    assert data_file.is_file(), "falta el archivo de datos externalizado data/criterios-precios.json"


def test_seo_geo_sin_nombres_en_sitemap_y_llms():
    """HU-WEB-016: sitemap.xml y llms.txt NO nombran plataformas competidoras
    (decisión 2026-07-29). Las keywords son genéricas."""
    root = Path(__file__).parent.parent
    for fname in ("sitemap.xml", "llms.txt"):
        text = (root / fname).read_text(encoding="utf-8")
        for nombre in ["Kommo", "Vambe", "Dapta", "Botpress", "ManyChat", "Chatfuel"]:
            assert nombre not in text, (
                f"{fname} nombra a {nombre} (decisión 2026-07-29: sin nombres en SEO/GEO)")
    # Sitemap incluye las páginas nuevas del paraguas
    sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
    for url in ["atencion-cliente", "criterios"]:
        assert url in sitemap, f"sitemap.xml no incluye /{url}"


def test_landing_pages_citables_por_asistentes_ia():
    """HU-WEB-016 AC2: las páginas con FAQ tienen schema JSON-LD FAQPage válido.
    Las páginas citable por asistentes de IA."""
    root = Path(__file__).parent.parent
    for fname in ("criterios.html", "atencion-cliente.html"):
        html = (root / fname).read_text(encoding="utf-8")
        assert "FAQPage" in html, f"{fname} sin schema FAQPage (no citable por IAs para preguntas)"
        assert "application/ld+json" in html, f"{fname} sin JSON-LD embebido"


@pytest.mark.parametrize("path", PAGES)
def test_links_internos_resuelven(mobile_page, path):
    """Todo href interno de una página pública apunta a un archivo del repo."""
    goto(mobile_page, path)
    hrefs = mobile_page.eval_on_selector_all(
        "a[href]", "els => els.map(e => e.getAttribute('href'))")
    root = Path(__file__).parent.parent
    rotos = []
    for h in set(hrefs):
        if not h or h.startswith(("http", "mailto:", "tel:", "#", "javascript:")):
            continue
        clean = h.lstrip("/").split("#")[0].split("?")[0]
        if clean.startswith("blog/") and clean != "blog/":
            continue  # posts Jekyll: los genera el build de Pages, no existen como archivo
        target = root / clean
        if target.is_dir() or clean.endswith("/") or clean == "":
            target = root / clean / "index.html"
        elif not target.suffix:
            target = root / f"{clean}.html"  # Pages resuelve /precios → precios.html
        if not target.exists():
            rotos.append(h)
    assert not rotos, f"links internos rotos en {path}: {rotos}"


# ──────────────── 4. REGRESIÓN DE REGISTRO (jerga prohibida) ────────────────

@pytest.mark.parametrize("path", [p for p in PAGES if p not in ("/privacidad.html", "/blog/")])
def test_registro_sin_jerga(mobile_page, path):
    """CLAUDE.md §Registro: lenguaje del emprendedor de a pie, cero jerga startup.
    privacidad (legal) y blog (posts viejos con valor SEO) quedan exentos."""
    goto(mobile_page, path)
    text = visible_text(mobile_page)
    hallazgos = [pat for pat in JERGA if re.search(pat, text, re.I)]
    m = ESCALAR_PROHIBIDO.search(text)
    if m:
        hallazgos.append(f"escalar[crecimiento]: '...{text[max(0,m.start()-30):m.end()+30]}...'")
    assert not hallazgos, f"{path} viola la regla de registro: {hallazgos}"


# ──────────────── 5. CONSISTENCIA COMERCIAL (precio único, demo 30) ────────────────

def test_precio_consistente():
    """Setup $250.000 (pago único) + mensualidad $250.000 en la página dedicada de precios.

    Ajuste de precio: el setup y la mensualidad pasaron a ser $250.000 CLP.
    El contrafactual es el valor antiguo $190.000: si vuelve a aparecer, el sitio quedó desalineado."""
    root = Path(__file__).parent.parent
    precios_html = (root / "precios.html").read_text(encoding="utf-8")
    assert "$250.000" in precios_html, "precios.html no menciona la tarifa $250.000"
    for f in ["index.html", "precios.html"]:
        html = (root / f).read_text(encoding="utf-8")
        assert "$190.000" not in html, f"{f} aún menciona el valor antiguo $190.000"


def test_json_ld_declara_la_mensualidad_vigente():
    """El Offer del JSON-LD alimenta los rich results de Google: si queda en el
    precio viejo, el buscador sigue publicando $190.000 aunque la página no lo muestre."""
    html = (Path(__file__).parent.parent / "index.html").read_text(encoding="utf-8")
    assert '"price": "250000"' in html, "el JSON-LD no declara la mensualidad vigente"
    assert '"price": "190000"' not in html, (
        "el JSON-LD aún declara $190.000: Google seguirá mostrando el precio viejo"
    )


def test_crm_va_incluido_en_la_mensualidad():
    """Decisión comercial 2026-07-30: el CRM entra en el plan, no se cobra aparte.
    Si vuelve a ofrecerse como módulo con costo, precios.html y crm.html se contradicen."""
    root = Path(__file__).parent.parent
    for f in ["index.html", "precios.html"]:
        html = (root / f).read_text(encoding="utf-8")
        assert "Módulo CRM" in html, f"{f} no declara el CRM dentro de lo incluido"
    data = json.loads((root / "data" / "criterios-precios.json").read_text(encoding="utf-8"))
    por_negocio = next(m for m in data["modelos"] if m["id"] == "por-negocio")
    assert por_negocio["precio_clp_mes"] == 250000
    assert not por_negocio["modulos_adicionales"], (
        "el CRM va incluido: no debe quedar listado como módulo adicional con precio aparte"
    )


def test_no_se_publica_material_comercial_descargable():
    """Decisión de Rodrigo (2026-07-31): el brochure no se comparte en ningún canal.

    GitHub Pages sirve cualquier archivo del repo, así que un PDF/PPTX suelto queda
    descargable aunque ninguna página lo enlace. Fue exactamente lo que pasó:
    `TheIA_Sales_Agent_v4.pdf` siguió respondiendo 200 en theia.cl durante meses
    después de sacarlo del hero, publicando la tarifa antigua.

    El contrafactual: si alguien vuelve a dejar material comercial en el repo,
    este test falla antes del deploy."""
    root = Path(__file__).parent.parent
    publicables = []
    for ext in ("*.pdf", "*.pptx", "*.ppt", "*.docx", "*.key"):
        for f in root.rglob(ext):
            if any(p in f.parts for p in (".git", ".venv-test", "node_modules")):
                continue
            publicables.append(f.relative_to(root))
    assert not publicables, (
        f"material descargable en el repo: {publicables}. GitHub Pages lo sirve "
        "público. El brochure y las propuestas no se publican en el sitio."
    )


def test_precios_explica_cargos_de_whatsapp_business():
    """El precio TheIA no debe prometer que el canal Meta es ilimitado o gratuito."""
    html = (Path(__file__).parent.parent / "precios.html").read_text(encoding="utf-8")
    assert "/terminos" in html, "precios debe enlazar los Términos de Servicio"
    assert "WhatsApp Business es un canal de terceros" in html
    assert "Sin cobro por conversación extra" not in html


def test_demo_es_30_minutos(mobile_page):
    """La demo es de 30 minutos (decisión documentada) — '15 minutos' no debe reaparecer."""
    for path in ("/", "/precios.html"):
        goto(mobile_page, path)
        text = visible_text(mobile_page)
        assert not re.search(r"15 minutos", text), f"{path} volvió a ofrecer demo de 15 minutos (es 30)"


@pytest.mark.parametrize("path", PAGES)
def test_widget_en_todas_las_paginas(mobile_page, path):
    """El webchat y su helper personalizado (/webchat-cta.js) deben estar en TODAS las páginas."""
    goto(mobile_page, path)
    content = mobile_page.content()
    assert "webchat-widget.js" in content, f"{path} sin el widget de webchat"
    assert "webchat-cta.js" in content, f"{path} sin el helper compartido webchat-cta.js"
    assert content.index("webchat-cta.js") < content.index("webchat-widget.js"), (
        f"{path}: webchat-cta.js debe cargarse antes que webchat-widget.js"
    )
    csp = mobile_page.eval_on_selector(
        "meta[http-equiv='Content-Security-Policy']",
        "el => el ? el.getAttribute('content') : ''") or ""
    script_src = ""
    for directive in csp.split(";"):
        if directive.strip().startswith("script-src"):
            script_src = directive
            break
    assert "admin.theia.cl" in script_src, (
        f"{path}: la CSP (script-src) no permite admin.theia.cl — el webchat quedaría bloqueado")


# ───────────────────────── 6. STICKY WHATSAPP EN MÓVIL ─────────────────────────

def test_sticky_whatsapp_movil(mobile_page):
    goto(mobile_page, "/")
    mobile_page.mouse.wheel(0, 1500)
    mobile_page.wait_for_timeout(300)
    stickies = mobile_page.eval_on_selector_all(
        "a[href*='wa.me']",
        """els => els.filter(e => {
            for (let n = e; n && n !== document.body; n = n.parentElement) {
                const cs = getComputedStyle(n);
                if (cs.position === 'fixed' && cs.display !== 'none' && cs.visibility !== 'hidden')
                    return true;
            }
            return false;
        }).length""")
    assert stickies >= 1, "no hay botón WhatsApp fijo (sticky) visible al scrollear en móvil"


def test_sticky_whatsapp_desktop(desktop_page):
    """Estilo Dapta.ai: en desktop hay un único widget flotante de atención (WebChat).
    El botón sticky-wa no debe duplicar flotantes en desktop y WhatsApp se accede
    orgánicamente desde navbar, CTAs y footer."""
    goto(desktop_page, "/")
    desktop_page.mouse.wheel(0, 1500)
    desktop_page.wait_for_timeout(300)
    is_hidden = desktop_page.evaluate("""() => {
        const wa = document.querySelector('.sticky-wa');
        if (!wa) return true;
        const cs = getComputedStyle(wa);
        return cs.display === 'none';
    }""")
    assert is_hidden, "en desktop .sticky-wa debe ser display:none para evitar colisión/duplicidad con el WebChat (estilo Dapta.ai)"


def test_sin_colision_entre_widgets_flotantes(desktop_page, mobile_page):
    """QA de Widgets Flotantes: verifica que el botón de WhatsApp (.sticky-wa) y el
    asistente WebChat (#theia-widget-btn) no se traslapen ni colisionen en teléfono ni escritorio."""
    for page, mode in [(desktop_page, "desktop"), (mobile_page, "mobile")]:
        goto(page, "/")
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(400)
        has_overlap = page.evaluate("""() => {
            const wa = document.querySelector('.sticky-wa');
            const chat = document.getElementById('theia-widget-btn');
            if (!wa || !chat) return false;
            const cs1 = getComputedStyle(wa);
            const cs2 = getComputedStyle(chat);
            if (cs1.display === 'none' || cs2.display === 'none') return false;
            const r1 = wa.getBoundingClientRect();
            const r2 = chat.getBoundingClientRect();
            if (r1.width === 0 || r1.height === 0 || r2.width === 0 || r2.height === 0) return false;
            return !(r1.right < r2.left || r1.left > r2.right || r1.bottom < r2.top || r1.top > r2.bottom);
        }""")
        assert not has_overlap, f"Colisión o traslape detectado entre .sticky-wa y #theia-widget-btn en modo {mode}"


@pytest.mark.parametrize("path", PAGES)
def test_webchat_frame_branding_and_contrast(mobile_page, path):
    """QA WebChat Frame en las 19 páginas públicas:
    1. Verifica que el header del widget (#theia-widget-header) no use el emoji '💬' crudo.
    2. Verifica que las respuestas rápidas (.theia-quick-replies button) no usen texto dorado claro sobre fondo blanco (bajo contraste).
    """
    goto(mobile_page, path)
    mobile_page.wait_for_timeout(600)

    btn = mobile_page.locator("#theia-widget-btn")
    if btn.is_visible():
        btn.evaluate("el => el.click()")
        mobile_page.wait_for_timeout(400)

    header_text = mobile_page.locator("#theia-widget-header").inner_text()
    assert "💬" not in header_text, f"{path}: el header del WebChat conserva el emoji '💬' crudo: {header_text!r}"

    reply_styles = mobile_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('.theia-quick-replies button'));
        return btns.map(b => {
            const cs = getComputedStyle(b);
            return { text: b.innerText, color: cs.color, bg: cs.backgroundColor };
        });
    }""")
    for item in reply_styles:
        assert item["color"] not in ("rgb(212, 175, 55)", "rgb(235, 202, 115)"), (
            f"{path}: bajo contraste en quick reply '{item['text']}': texto dorado {item['color']} sobre {item['bg']}"
        )


# ───────────────── 7. EVIDENCIA VISUAL (screenshots → artifacts CI) ─────────────────

def screenshot_name(path):
    if path == "/":
        return "index"
    if path == "/blog/":
        return "blog"
    return path.strip("/").removesuffix(".html")


@pytest.mark.parametrize("path", PAGES)
def test_screenshots_mobile(mobile_page, path):
    goto(mobile_page, path)
    mobile_page.wait_for_timeout(600)
    mobile_page.screenshot(path=str(SHOTS / f"{screenshot_name(path)}-mobile.png"), full_page=True)


def test_screenshot_hero_desktop(desktop_page):
    goto(desktop_page, "/")
    desktop_page.wait_for_timeout(600)
    desktop_page.screenshot(path=str(SHOTS / "index-desktop-hero.png"))


def test_screenshot_funciones_desktop(desktop_page):
    goto(desktop_page, "/funciones.html")
    desktop_page.wait_for_timeout(600)
    desktop_page.screenshot(path=str(SHOTS / "funciones-desktop-hero.png"))


def test_screenshot_casos_desktop(desktop_page):
    goto(desktop_page, "/casos.html")
    desktop_page.wait_for_timeout(600)
    desktop_page.screenshot(path=str(SHOTS / "casos-desktop-hero.png"))


# ──────────────── 6. QA DE FRONTEND ROBUSTO (imágenes, navbar, padding, botones, emojis) ────────────────

MARKETING_PAGES = [p for p in PAGES if p not in ["/cumplimiento.html", "/privacidad.html", "/terminos.html"]]


@pytest.mark.parametrize("path", PAGES)
def test_todas_las_imagenes_locales_cargan_en_browser(mobile_page, path):
    """QA de Imágenes: verifica que cada <img> de origen local cargue correctamente sin 404 ni naturalWidth == 0."""
    goto(mobile_page, path)
    broken_imgs = mobile_page.evaluate("""() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        return imgs.filter(img => {
            const isLocal = img.src.includes('127.0.0.1') || img.src.includes('theia.cl') || img.src.startsWith('file:');
            return isLocal && (!img.complete || img.naturalWidth === 0);
        }).map(img => img.src);
    }""")
    assert not broken_imgs, f"{path} tiene imágenes locales rotas que no cargan: {broken_imgs}"


@pytest.mark.parametrize("path", MARKETING_PAGES)
def test_homologacion_de_navbar_y_logo(mobile_page, path):
    """QA de Nav: verifica logo responsive (60px/100px) y los 8 enlaces de navegación homologados."""
    goto(mobile_page, path)
    logo_height = mobile_page.evaluate("""() => {
        const logoImg = document.querySelector('.logo img');
        return logoImg ? getComputedStyle(logoImg).height : '0px';
    }""")
    assert logo_height in ["60px", "100px"], f"{path} tiene la altura del logo fuera de norma (altura: {logo_height})"

    nav_texts = mobile_page.evaluate("""() => {
        const links = Array.from(document.querySelectorAll('.nav-cta a'));
        return links.map(a => a.innerText.trim());
    }""")
    expected = ["Atención", "Cómo ayuda", "CRM", "Plataforma", "Precios", "Recursos", "Agenda una demo →"]
    for item in expected:
        assert item in nav_texts, f"{path} no contiene el enlace de navegación homologado '{item}': {nav_texts}"


@pytest.mark.parametrize("path", PAGES)
def test_secciones_tienen_padding_y_sin_colision(mobile_page, path):
    """QA de Spacing: verifica que cada <section> tenga padding suficiente arriba y abajo."""
    goto(mobile_page, path)
    cramped_sections = mobile_page.evaluate("""() => {
        const sections = Array.from(document.querySelectorAll('section:not(#network-canvas)'));
        return sections.filter(sec => {
            const style = getComputedStyle(sec);
            const pt = parseInt(style.paddingTop, 10);
            const pb = parseInt(style.paddingBottom, 10);
            return (pt < 15 || pb < 15) && !sec.classList.contains('metrics-banner');
        }).map(sec => sec.className || sec.id || 'unnamed section');
    }""")
    assert not cramped_sections, f"{path} tiene secciones colapsadas sin padding adecuado: {cramped_sections}"


@pytest.mark.parametrize("path", PAGES)
def test_sin_botones_con_borde_negro_browser(mobile_page, path):
    """QA de Botones: verifica que ningún <button> tenga el borde negro por defecto del navegador."""
    goto(mobile_page, path)
    glitched_buttons = mobile_page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button.btn'));
        return btns.filter(btn => {
            const style = getComputedStyle(btn);
            return style.borderStyle === 'solid' && (style.borderColor === 'rgb(0, 0, 0)' || style.borderColor === 'canvastext');
        }).map(btn => btn.innerText.trim());
    }""")
    assert not glitched_buttons, f"{path} contiene botones con borde negro de navegador: {glitched_buttons}"


@pytest.mark.parametrize("path", PAGES)
def test_sin_emojis_crudos_en_encabezados_y_tarjetas(path):
    """QA Visual: asegura que no se usen emojis de texto como íconos principales de tarjetas."""
    root = Path(__file__).parent.parent
    rel = path.lstrip("/")
    file_path = root / rel
    if file_path.is_dir():
        file_path = file_path / "index.html"
    content = file_path.read_text(encoding="utf-8")
    raw_emojis = re.findall(r"<div[^>]*font-size:\s*2rem[^>]*>[💬📊📋⚙️🔒📜🔑💰🚫🤝]", content)
    assert not raw_emojis, f"{path} tiene íconos de tarjetas con emojis crudos desalineados: {raw_emojis}"
