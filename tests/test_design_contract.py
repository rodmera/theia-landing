"""Contratos del look & feel y de verdad comercial de theia.cl.

Estos tests cubren reglas que una captura aislada no puede demostrar: familias
tipográficas, pesos realmente cargados, navegación semántica y promesas de CRM.
"""
import re
from pathlib import Path

import pytest

from conftest import BASE, PAGES


ROOT = Path(__file__).resolve().parent.parent
CANONICAL_FONT_URL = (
    "family=Merriweather:wght@700;900&family=Plus+Jakarta+Sans:wght@400;500;700"
)
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}]+)", re.I)
FONT_SHORTHAND = re.compile(r"\bfont\s*:\s*([^;}]+)", re.I)
NUMERIC_WEIGHT = re.compile(r"font-weight\s*:\s*(\d+)\b", re.I)
CANONICAL_FAMILIES = {
    "merriweather": {"700", "900"},
    "plus jakarta sans": {"400", "500", "700"},
}
CANONICAL_FONT_DECLARATIONS = {
    "inherit",
    "merriweather,serif",
    "plusjakartasans,sans-serif",
}
SITE_HTML = [
    *ROOT.glob("*.html"),
    ROOT / "blog" / "index.html",
    ROOT / "_layouts" / "post.html",
]


def public_source(path):
    if path == "/":
        return ROOT / "index.html"
    if path == "/blog/":
        return ROOT / "blog" / "index.html"
    return ROOT / path.lstrip("/")


def line_number(source, offset):
    return source.count("\n", 0, offset) + 1


def compact_font_declaration(value):
    return re.sub(r"[\s'\"]", "", value.lower())


def test_cada_pagina_publica_carga_las_fuentes_canonicas():
    missing = []
    for path in PAGES:
        file = public_source(path)
        source = file.read_text(encoding="utf-8")
        if CANONICAL_FONT_URL not in source:
            missing.append(str(file.relative_to(ROOT)))
    assert not missing, f"páginas sin las fuentes canónicas: {missing}"


def test_no_hay_familias_tipograficas_fuera_del_sistema():
    findings = []
    for file in SITE_HTML:
        source = file.read_text(encoding="utf-8")
        for match in FONT_FAMILY.finditer(source):
            value = compact_font_declaration(match.group(1))
            if value not in CANONICAL_FONT_DECLARATIONS:
                findings.append(f"{file.relative_to(ROOT)}:{line_number(source, match.start())} → {match.group()}")
        for match in FONT_SHORTHAND.finditer(source):
            value = compact_font_declaration(match.group(1))
            if "font-family" not in match.group(0).lower() and not any(
                value.endswith(declaration) for declaration in CANONICAL_FONT_DECLARATIONS - {"inherit"}
            ):
                findings.append(f"{file.relative_to(ROOT)}:{line_number(source, match.start())} → {match.group()}")
    assert not findings, "familias tipográficas no permitidas:\n" + "\n".join(findings)


def test_no_hay_pesos_tipograficos_no_cargados():
    findings = []
    for file in SITE_HTML:
        source = file.read_text(encoding="utf-8")
        for match in NUMERIC_WEIGHT.finditer(source):
            if match.group(1) not in {"400", "500", "700", "900"}:
                findings.append(f"{file.relative_to(ROOT)}:{line_number(source, match.start())} → {match.group()}")
    assert not findings, "pesos tipográficos no cargados:\n" + "\n".join(findings)


def test_plataforma_nunca_enlaza_al_producto_pulse():
    bad_links = []
    pattern = re.compile(r'<a\s+href="/pulse"[^>]*>\s*Plataforma\s*</a>', re.I)
    for file in ROOT.glob("*.html"):
        source = file.read_text(encoding="utf-8")
        if pattern.search(source):
            bad_links.append(file.name)
    assert not bad_links, f"rótulo Plataforma apunta a /pulse: {bad_links}"


def test_omnicanal_no_aparece_en_copy_visible_de_home():
    """Decisión estratégica 2026-07-29: usar canales concretos, no jerga visible."""
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    assert not re.search(r">\s*Omnicanal\s*<", source, re.I)


def test_crm_no_se_ofrece_como_funcionalidad_lista():
    """CRM aún no tiene empaquetado, precio ni lead scoring en producción."""
    forbidden = [
        "CRM con pipeline automático",
        "lead scoring",
        "viaje del cliente en 5 etapas",
        "valor de deals",
    ]
    findings = []
    for filename in ("index.html", "precios.html"):
        source = (ROOT / filename).read_text(encoding="utf-8").lower()
        findings.extend(f"{filename}: {claim}" for claim in forbidden if claim.lower() in source)
    assert not findings, "promesas CRM no habilitadas:\n" + "\n".join(findings)


def test_ctas_crm_usan_openTheiaChat():
    """HU-WEB-027: Los CTAs de prueba en vivo de CRM (crm.html) deben invocar el helper
    compartido openTheiaChat('crm'), mientras que las tarjetas paraguas en index.html y
    atencion-cliente.html usan enlace canónico a /crm.
    """
    expected = "openTheiaChat('crm')"
    stale_inline = ("theiaChatOpen('crm')", 'theiaChatOpen("crm")')
    findings = []
    # crm.html usa el helper compartido para probar en vivo
    source_crm = (ROOT / "crm.html").read_text(encoding="utf-8")
    if expected not in source_crm:
        findings.append(f"crm.html no llama {expected}")
    for stale in stale_inline:
        if stale in source_crm:
            findings.append(f"crm.html aún tiene la forma inline {stale!r}")

    # index.html y atencion-cliente.html usan enlace canónico a /crm (HU-WEB-027 AC1)
    for filename in ("index.html", "atencion-cliente.html"):
        source = (ROOT / filename).read_text(encoding="utf-8")
        if 'href="/crm"' not in source:
            findings.append(f"{filename} debe contener enlace canónico href='/crm'")
        for stale in stale_inline:
            if stale in source:
                findings.append(f"{filename} aún tiene la forma inline {stale!r}")
    assert not findings, "CTAs CRM no cumplen con el contrato:\n" + "\n".join(findings)


def test_no_promesa_de_futuro_en_copy_visible():
    """Decisión 2026-07-30 (contexto post-PLAI): 'próximamente / soon' queda
    PROHIBIDO en copy visible. Una feature que aún no está en producción:
      - no se etiqueta como futura;
      - no se ofrece con CTA que comunica futuro (Avísame, etc.);
      - se omite hasta estar en producción (criterio AC2 de HU-WEB-012).

    El arnés cubre TODO el HTML público (PAGES + blog + layouts). Si una
    feature vuelve al backlog o cambia de scope, CI bloquea cualquier
    regresión de copy que la siga prometiendo como futura.

    Nota: 'te avisamos' en contexto de cupo/operación (no de feature) es
    legítimo y queda fuera del arnés — el contrato es semántico, no léxico.
    """
    forbidden = [
        "próximamente",
        "próximas",
        "avísame",
        "en camino",
        "coming soon",
    ]
    findings = []
    for file in SITE_HTML:
        if not file.exists():
            continue
        source = file.read_text(encoding="utf-8")
        for marker in forbidden:
            for match in re.finditer(re.escape(marker), source, re.I):
                findings.append(
                    f"{file.relative_to(ROOT)}:{line_number(source, match.start())} → "
                    f"{match.group()!r} (copy visible promete futuro)"
                )
    # "soon" como palabra suelta (case-insensitive, word-boundary).
    for file in SITE_HTML:
        if not file.exists():
            continue
        source = file.read_text(encoding="utf-8")
        for match in re.finditer(r"\bsoon\b", source, re.I):
            findings.append(
                f"{file.relative_to(ROOT)}:{line_number(source, match.start())} → "
                f"{match.group()!r} (copy visible promete futuro)"
            )
    assert not findings, "copy visible promete futuro:\n" + "\n".join(findings)


def test_hero_de_home_usa_imagen_conceptual_de_orquestacion_sin_interfaz_ficticia():
    """El hero comunica orquestación agéntica con un flujo dinámico para PYMEs, no una app simulada."""
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    hero = source[source.index('<section class="hero"'):source.index("</section>", source.index('<section class="hero"'))]
    for marker in ("hero-orchestration-visual", "TheIA Core", "Agente Catálogo", "Agente Agenda", "Agente CRM"):
        assert marker in hero, f"hero perdió el componente visual obligatorio: {marker}"
    for stale in ("hero-console", "hero-stage-", "client-header", "client-channels"):
        assert stale not in hero, f"hero conserva interfaz ficticia: {stale}"


def test_hero_orquestacion_respeta_la_composicion_desktop_y_mobile(desktop_page, mobile_page):
    """La pieza editorial queda a la derecha en desktop y se renderiza responsivamente en teléfono."""
    desktop_page.goto(BASE, wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(300)
    heading = desktop_page.locator(".hero h1").bounding_box()
    visual = desktop_page.locator(".hero-orchestration-visual").bounding_box()
    assert heading and visual, "hero sin título o imagen conceptual en desktop"
    assert visual["x"] > heading["x"] + heading["width"] * 0.75, "imagen conceptual no queda al lado del mensaje"

    mobile_page.goto(BASE, wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(300)
    display = mobile_page.locator(".hero-orchestration-visual").evaluate("el => getComputedStyle(el).display")
    assert display != "none", f"imagen conceptual debe mostrarse en móvil, no {display}"
    mob_visual = mobile_page.locator(".hero-orchestration-visual").bounding_box()
    mob_heading = mobile_page.locator(".hero h1").bounding_box()
    assert mob_visual and mob_heading, "hero sin elementos en móvil"
    assert mob_visual["y"] > mob_heading["y"], "apoyo visual debe ubicarse debajo del título en móvil"
    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    client_w = mobile_page.evaluate("document.documentElement.clientWidth")
    assert scroll_w <= client_w, f"Desbordamiento horizontal en móvil: {scroll_w} > {client_w}"

@pytest.mark.parametrize("path", PAGES)
def test_roles_tipograficos_se_renderizan_en_el_navegador(mobile_page, path):
    """Verifica las font faces cargadas y sus pesos sobre el DOM realmente renderizado."""
    import time
    mobile_page.goto(BASE + path, wait_until="domcontentloaded")
    # Espera determinista: reintenta hasta que ambas familias canónicas estén en estado 'loaded'
    start = time.time()
    while time.time() - start < 15:
        ready = mobile_page.evaluate("""() => {
            document.fonts.load('900 16px Merriweather');
            document.fonts.load('400 16px "Plus Jakarta Sans"');
            document.fonts.load('700 16px "Plus Jakarta Sans"');
            const faces = [...document.fonts];
            const loadedFamily = fam => faces.some(
                f => f.family.replaceAll('"', '').replaceAll("'", '').toLowerCase().includes(fam)
                     && f.status === 'loaded'
            );
            return loadedFamily('merriweather') && loadedFamily('plus jakarta sans');
        }""")
        if ready:
            break
        time.sleep(0.1)
    state = mobile_page.evaluate("""async () => {
        const loaded = [...document.fonts].filter(face => face.status === 'loaded').map(face => ({
            family: face.family.replaceAll('\\"', '').replaceAll("'", '').toLowerCase(),
            weight: face.weight,
        }));
        const roleElements = document.querySelectorAll(
            'body, h1, h2, h3, h4, .btn, .btn-gold, .btn-ghost, .btn-whatsapp'
        );
        const violations = [...roleElements].flatMap(element => {
            const style = getComputedStyle(element);
            const family = style.fontFamily.toLowerCase();
            const weight = style.fontWeight;
            if (family.includes('plus jakarta sans') && !['400', '500', '700'].includes(weight)) {
                return [`Plus Jakarta ${weight} en <${element.tagName.toLowerCase()}>`];
            }
            if (family.includes('merriweather') && !['700', '900'].includes(weight)) {
                return [`Merriweather ${weight} en <${element.tagName.toLowerCase()}>`];
            }
            return [];
        });
        return { loaded, violations };
    }""")
    assert any("plus jakarta sans" in face["family"] for face in state["loaded"]), (
        f"{path} no cargó Plus Jakarta Sans: {state['loaded']}"
    )
    assert any("merriweather" in face["family"] for face in state["loaded"]), (
        f"{path} no cargó Merriweather: {state['loaded']}"
    )
    assert not state["violations"], f"{path} usa pesos renderizados inválidos: {state['violations'][:5]}"


SUBTITULO_CANONICO_REM = "1.05rem"
SUBTITULO_CANONICO_PX = "16.8px"  # 1.05rem a font-size raíz 16px
SUBTITULO_SELECTORES = (
    ".hero-sub", ".section-sub", ".price-tagline", ".subtitle", ".lead",
    ".crm-hero p", ".pulse-hero p",
)
# Páginas legales (subtítulo de fecha, diseño propio) y blog Jekyll (otra
# estructura): el contrato de subtítulo de hero aplica a las de marketing.
SUBTITULO_EXCLUIDAS = {"/privacidad.html", "/terminos.html", "/blog/"}


def _subtitulo_hero(mobile_page, path):
    """Devuelve el font-size renderizado del subtítulo bajo el H1 del hero."""
    mobile_page.goto(BASE + path, wait_until="domcontentloaded")
    return mobile_page.evaluate("""() => {
        const h = document.querySelector('h1');
        if (!h) return { fs: null, why: 'sin h1' };
        let p = h.nextElementSibling;
        if (!p || !p.textContent.trim()) {
            const sels = %(sels)r;
            p = sels.map(s => h.parentElement && h.parentElement.querySelector(s))
                    .find(el => el && el.textContent.trim());
        }
        if (!p) return { fs: null, why: 'sin subtítulo visible' };
        return { fs: getComputedStyle(p).fontSize, why: null };
    }""" % {"sels": list(SUBTITULO_SELECTORES)})


@pytest.mark.parametrize("path", PAGES)
def test_subtitulo_hero_tamano_consistente_entre_paginas(mobile_page, path):
    """Regresión 2026-08-10: los subtítulos de las páginas interiores tenían
    hasta 6 tamaños distintos (0.95rem a 1.2rem) y ningún test lo detectaba.
    Contrato: el subtítulo del hero renderiza a 1.05rem (16.8px) en todas las
    páginas de marketing."""
    if path in SUBTITULO_EXCLUIDAS:
        pytest.skip(f"{path}: página legal/blog, diseño propio")
    res = _subtitulo_hero(mobile_page, path)
    assert res["fs"], f"{path}: {res['why']}"
    assert res["fs"] == SUBTITULO_CANONICO_PX, (
        f"{path}: subtítulo del hero renderiza a {res['fs']}, "
        f"debe ser {SUBTITULO_CANONICO_REM} ({SUBTITULO_CANONICO_PX})"
    )


@pytest.mark.parametrize("path", PAGES)
def test_cards_glass_tipografia_consistente(mobile_page, path):
    """Regresión 2026-08-10: la sección '¿Por qué TheIA?' de precios.html usaba
    divs con estilos inline ad-hoc (icono 40px, títulos sans-serif, sin
    glass-card) que no seguían el sistema de diseño. Contrato: toda card del
    sitio usa .glass-card, icono canónico (.piece-icon-wrap 50px) y, dentro de
    cada grid, los títulos comparten tamaño y fuente Merriweather."""
    mobile_page.goto(BASE + path, wait_until="domcontentloaded")
    state = mobile_page.evaluate("""() => {
        const cards = [...document.querySelectorAll('.glass-card')];
        const outliers = [];
        for (const card of cards) {
            const icon = card.querySelector('.piece-icon-wrap');
            if (icon) {
                const w = Math.round(icon.getBoundingClientRect().width);
                if (w !== 50 && w !== 52) outliers.push(`icono ${w}px (no 50 o 52)`);
            }
            const h = card.querySelector('h3');
            if (h && !getComputedStyle(h).fontFamily.toLowerCase().includes('merriweather')) {
                outliers.push(`título no-Merriweather: ${h.textContent.trim().slice(0, 24)}`);
            }
        }
        // consistencia de tamaño de título DENTRO de cada grid hermano
        const grids = [...document.querySelectorAll('div[style*="grid"], .pricing-cards, .pieces-grid')];
        for (const grid of grids) {
            const tfs = [...grid.querySelectorAll(':scope > .glass-card h3')]
                .map(x => getComputedStyle(x).fontSize);
            const uniq = [...new Set(tfs)];
            if (uniq.length > 1) {
                outliers.push(`grid con títulos de tamaños mixtos: ${uniq.join(', ')}`);
            }
        }
        return { count: cards.length, outliers };
    }""")
    if state["count"]:
        assert not state["outliers"], f"{path}: cards con estilo no canónico: {state['outliers'][:6]}"


@pytest.mark.parametrize("path", PAGES)
def test_paleta_verde_restringida_a_whatsapp_y_status_dot(mobile_page, path):
    """Regla dura 2026-08-31: El verde (#34c77b / #25D366) NO es color de acento de marca (es TheIA Gold).
    El verde queda ESTRICTAMENTE restringido a:
      1. Icono/botón oficial de WhatsApp (.btn-whatsapp, .footer-contact-badge--wa, fill/stroke de logo WA)
      2. Micro-punto indicador de estado de 6px (● "En línea" / "En vivo")
    Prohibido usar verde en titulares, subtítulos, precios, cifras monetarias, cantidades,
    bordes de tarjetas o pastillas promocionales.
    """
    mobile_page.goto(BASE + path, wait_until="domcontentloaded")
    violations = mobile_page.evaluate("""() => {
        const issues = [];
        const allElements = document.querySelectorAll('h1, h2, h3, h4, strong, p, span, div, a');
        for (const el of allElements) {
            // Ignorar elementos de WhatsApp y status dots
            if (el.closest('.btn-whatsapp, .footer-contact-badge--wa, .footer-bottom-wa, #theia-widget-btn, .chat-online, .badge-dot, .live-dot')) {
                continue;
            }
            if (el.classList.contains('btn-whatsapp') || el.classList.contains('badge-dot') || el.classList.contains('live-dot')) {
                continue;
            }
            // Ignorar SVGs de logos oficiales
            if (el.closest('svg') || el.tagName.toLowerCase() === 'svg') {
                continue;
            }

            const style = getComputedStyle(el);
            const color = style.color;
            const bg = style.backgroundColor;
            const border = style.borderColor;

            // Detectar verdes (#34c77b = rgb(52, 199, 123), #25D366 = rgb(37, 211, 102), #10b981 = rgb(16, 185, 129))
            const isGreen = str => {
                if (!str) return false;
                const s = str.toLowerCase();
                return s.includes('52, 199, 123') || s.includes('37, 211, 102') || s.includes('16, 185, 129') || s.includes('#34c77b') || s.includes('#25d366') || s.includes('#10b981');
            };

            if (isGreen(color)) {
                issues.push(`Texto verde en <${el.tagName.toLowerCase()}> "${el.textContent.trim().slice(0, 30)}": ${color}`);
            }
        }
        return issues;
    }""")
    assert not violations, f"{path}: elementos con verde no autorizado:\n" + "\n".join(violations[:10])


@pytest.mark.parametrize("path", PAGES)
def test_dash_badges_conformes_a_theia_gold(mobile_page, path):
    """Regla dura de Design System: Los .dash-badge (eyebrows/pastillas de sección)
    deben usar paleta TheIA Gold (color dorado / gold-light) y fondos dorados sutiles,
    PROHIBIENDO el uso de tonos morados / índigo (#4f46e5 / #818cf8 / rgb(79, 70, 229)).
    """
    mobile_page.goto(BASE + path, wait_until="domcontentloaded")
    violations = mobile_page.evaluate("""() => {
        const issues = [];
        const badges = document.querySelectorAll('.dash-badge');
        for (const badge of badges) {
            const style = getComputedStyle(badge);
            const color = style.color;
            const bg = style.backgroundColor;
            const border = style.borderColor;

            // Detectar morados / índigos (79, 70, 229 o 129, 140, 248)
            const isPurple = str => {
                if (!str) return false;
                const s = str.toLowerCase();
                return s.includes('79, 70, 229') || s.includes('129, 140, 248') || s.includes('99, 102, 241') || s.includes('168, 85, 247');
            };

            if (isPurple(color) || isPurple(bg) || isPurple(border)) {
                issues.push(`Badge morado no conforme en "${badge.textContent.trim().slice(0, 30)}": color=${color}, bg=${bg}, border=${border}`);
            }
        }
        return issues;
    }""")
    assert not violations, f"{path}: .dash-badge con morado/índigo no autorizado:\n" + "\n".join(violations[:10])


def test_static_no_hay_overrides_inline_ni_css_en_titulos():
    """Design System Regla Dura (2026-09-04): Los títulos de sección (h2, .section-title)
    deben seguir deterministamente el sistema de diseño central.
    Está PROHIBIDO el uso de estilos inline con font-size o font-weight en h1/h2,
    así como overrides en archivos CSS secundarios que reduzcan el peso a 700 o
    desalineen la escala clamp(2rem, 3.5vw, 3rem).
    """
    violations = []
    # 1. Chequeo de estilos inline en HTML
    for file in SITE_HTML:
        if not file.exists():
            continue
        source = file.read_text(encoding="utf-8")
        for match in re.finditer(r'<h[12][^>]*style="[^"]*(?:font-size|font-weight)[^"]*"[^>]*>', source, re.I):
            violations.append(f"{file.relative_to(ROOT)}:{line_number(source, match.start())} → {match.group()!r}")

    # 2. Chequeo de CSS secundarios para evitar overrides no autorizados en .section-title
    for css_file in ROOT.glob("*.css"):
        source = css_file.read_text(encoding="utf-8")
        for match in re.finditer(r'([^{]+)\{\s*[^}]*font-weight\s*:\s*700[^}]*\}', source, re.I):
            selector = match.group(1).strip()
            if "section-title" in selector or "-header h2" in selector:
                violations.append(f"{css_file.relative_to(ROOT)}: override no permitido en {selector!r} con font-weight: 700")
    assert not violations, "Overrides no permitidos en títulos de sección:\n" + "\n".join(violations)


@pytest.mark.parametrize("path", PAGES)
def test_titulos_de_seccion_homologados_estrictamente(desktop_page, path):
    """Design System Regla Dura (2026-09-04): TODOS los títulos de sección (.section-title)
    en todas las páginas de marketing deben computar exactamente:
      - font-family: Merriweather
      - font-weight: 900 (PROHIBIDO degradar a 700 en títulos de sección)
      - color: blanco (#ffffff)
      - span.gold / .gold: #d4af37 (TheIA Gold, PROHIBIDO #ebca73 o colores deslavados)
      - font-size: clamp(2rem, 3.5vw, 3rem) -> entre 40px y 48px en desktop
      - line-height: 1.2
    """
    if path in SUBTITULO_EXCLUIDAS:
        pytest.skip(f"{path}: página legal/blog, estructura propia")
    desktop_page.goto(BASE + path, wait_until="domcontentloaded")
    violations = desktop_page.evaluate("""() => {
        const issues = [];
        const headings = [...document.querySelectorAll('.section-title')].filter(el => !el.closest('[hidden]'));
        for (const h of headings) {
            const cs = getComputedStyle(h);
            const fam = cs.fontFamily.toLowerCase();
            const weight = cs.fontWeight;
            const size = parseFloat(cs.fontSize);
            const color = cs.color;

            if (!fam.includes('merriweather')) {
                issues.push(`"${h.textContent.trim().slice(0, 30)}": familia no Merriweather (${cs.fontFamily})`);
            }
            if (weight !== '900') {
                issues.push(`"${h.textContent.trim().slice(0, 30)}": peso ${weight} (debe ser 900)`);
            }
            if (size < 38 || size > 49) {
                issues.push(`"${h.textContent.trim().slice(0, 30)}": tamaño ${size}px fuera del clamp(2rem, 3.5vw, 3rem)`);
            }
            if (color !== 'rgb(255, 255, 255)') {
                issues.push(`"${h.textContent.trim().slice(0, 30)}": color ${color} (debe ser blanco rgb(255, 255, 255))`);
            }

            // Validar spans dorados dentro del título
            const goldSpans = h.querySelectorAll('.gold, span.gold');
            for (const g of goldSpans) {
                const gc = getComputedStyle(g).color;
                if (!gc.includes('212, 175, 55')) {
                    issues.push(`"${h.textContent.trim().slice(0, 30)}" span dorado con color ${gc} (debe ser TheIA Gold rgb(212, 175, 55))`);
                }
            }
        }
        return issues;
    }""")
    assert not violations, f"{path}: títulos de sección no conformes:\n" + "\n".join(violations)


@pytest.mark.parametrize("path", PAGES)
def test_subtitulos_de_seccion_homologados_estrictamente(desktop_page, path):
    """Design System Regla Dura (2026-09-04): TODOS los subtítulos (.section-sub)
    en todas las páginas de marketing deben computar:
      - font-family: Plus Jakarta Sans
      - font-weight: 400 o 500
      - font-size: 1.05rem (16.8px)
      - max-width: <= 680px
    """
    if path in SUBTITULO_EXCLUIDAS:
        pytest.skip(f"{path}: página legal/blog, estructura propia")
    desktop_page.goto(BASE + path, wait_until="domcontentloaded")
    violations = desktop_page.evaluate("""() => {
        const issues = [];
        const subs = [...document.querySelectorAll('.section-sub')].filter(el => !el.closest('[hidden]'));
        for (const s of subs) {
            const cs = getComputedStyle(s);
            const fam = cs.fontFamily.toLowerCase();
            const weight = cs.fontWeight;
            const size = cs.fontSize;
            const maxW = parseFloat(cs.maxWidth);

            if (!fam.includes('plus jakarta sans')) {
                issues.push(`"${s.textContent.trim().slice(0, 30)}": familia no Plus Jakarta Sans (${cs.fontFamily})`);
            }
            if (weight !== '400' && weight !== '500') {
                issues.push(`"${s.textContent.trim().slice(0, 30)}": peso ${weight} (debe ser 400 o 500)`);
            }
            if (size !== '16.8px') {
                issues.push(`"${s.textContent.trim().slice(0, 30)}": tamaño ${size} (debe ser 16.8px / 1.05rem)`);
            }
            if (maxW > 685) {
                issues.push(`"${s.textContent.trim().slice(0, 30)}": max-width ${maxW}px excede 680px`);
            }
        }
        return issues;
    }""")
    assert not violations, f"{path}: subtítulos de sección no conformes:\n" + "\n".join(violations)


def test_svg_attributes_validity():
    """Verifica que ningún elemento <svg> contenga atributos XML no válidos como width='auto' o height='auto'.
    En la especificación W3C SVG 1.1/2, 'auto' es un valor de CSS, no un valor válido de atributo XML, y lanza
    un error de parser en la consola de Chromium: Error: <svg> attribute height: Expected length, 'auto'.
    """
    violations = []
    for file in SITE_HTML:
        if not file.is_file():
            continue
        content = file.read_text(encoding="utf-8")
        svg_tags = re.findall(r"<svg\b[^>]*>", content, re.I)
        for tag in svg_tags:
            if re.search(r'\b(?:width|height)\s*=\s*["\']auto["\']', tag, re.I):
                violations.append(
                    f"{file.name}: <svg> contiene width='auto' o height='auto' no válido en XML SVG. "
                    f"Debe utilizarse CSS 'style=\"height: auto;\"' en su lugar:\n  {tag[:120]}"
                )
    assert not violations, "Elementos SVG con atributos inválidos:\n" + "\n".join(violations)



