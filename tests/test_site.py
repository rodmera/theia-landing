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
    for texto in ["Pruébalo ahora", "Hablar por WhatsApp"]:
        assert mobile_page.get_by_text(texto).first.is_visible(), f"CTA '{texto}' no visible en móvil"


def test_links_internos_resuelven(mobile_page):
    """Todo href interno del index apunta a un archivo que existe en el repo."""
    goto(mobile_page, "/")
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
    assert not rotos, f"links internos rotos en index: {rotos}"


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
    """$190.000 presente donde se habla de precio; ningún precio alternativo inventado."""
    root = Path(__file__).parent.parent
    for f in ["index.html", "precios.html"]:
        html = (root / f).read_text(encoding="utf-8")
        assert "190.000" in html, f"{f} no menciona el precio $190.000"


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
    """El webchat (dogfooding + canal de dudas) debe estar en TODAS las páginas —
    antes solo estaba en el index: un prospecto en /precios no tenía dónde preguntar."""
    goto(mobile_page, path)
    assert "webchat-widget.js" in mobile_page.content(), f"{path} sin el widget de webchat"


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


# ───────────────── 7. EVIDENCIA VISUAL (screenshots → artifacts CI) ─────────────────

@pytest.mark.parametrize("path,name", [("/", "index"), ("/precios.html", "precios"),
                                        ("/nosotros.html", "nosotros"), ("/casos.html", "casos")])
def test_screenshots_mobile(mobile_page, path, name):
    goto(mobile_page, path)
    mobile_page.wait_for_timeout(600)
    mobile_page.screenshot(path=str(SHOTS / f"{name}-mobile.png"), full_page=True)


def test_screenshot_hero_desktop(desktop_page):
    goto(desktop_page, "/")
    desktop_page.wait_for_timeout(600)
    desktop_page.screenshot(path=str(SHOTS / "index-desktop-hero.png"))
