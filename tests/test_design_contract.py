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


def test_hero_de_home_mantiene_la_vista_360_y_los_iconos_oficiales():
    """El hero comunica un producto de atención, no una conversación simulada."""
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    hero = source[source.index('<section class="hero"'):source.index("</section>", source.index('<section class="hero"'))]
    for marker in ("client-header", "client-channels", "client-context", "#25D366", "#E1306C", "#6366F1"):
        assert marker in hero, f"hero perdió el componente visual obligatorio: {marker}"
    assert "chat-bubble" not in hero.lower(), "hero volvió a usar burbujas de chat simuladas"


def test_hero_360_respeta_la_composicion_desktop_y_mobile(desktop_page, mobile_page):
    """Relación visual estable: panel a la derecha en desktop, oculto en teléfono."""
    desktop_page.goto(BASE, wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(300)
    heading = desktop_page.locator(".hero h1").bounding_box()
    panel = desktop_page.locator(".hero-glass-card").bounding_box()
    assert heading and panel, "hero sin título o panel Vista 360 en desktop"
    assert panel["x"] > heading["x"] + heading["width"] * 0.75, "panel Vista 360 no queda al lado del mensaje"

    mobile_page.goto(BASE, wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(300)
    display = mobile_page.locator(".hero-glass-card").evaluate("el => getComputedStyle(el).display")
    assert display == "none", f"panel Vista 360 debe ocultarse en móvil, no {display}"


@pytest.mark.parametrize("path", PAGES)
def test_roles_tipograficos_se_renderizan_en_el_navegador(mobile_page, path):
    """Verifica las font faces cargadas y sus pesos sobre el DOM realmente renderizado."""
    mobile_page.goto(BASE + path, wait_until="domcontentloaded")
    state = mobile_page.evaluate("""async () => {
        await document.fonts.ready;
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
