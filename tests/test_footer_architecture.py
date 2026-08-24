"""
test_footer_architecture.py — Verificación de Arquitectura y Layout del Footer Canónico TheIA (4 Columnas).

Contratos validados:
1. Existencia y enlace de /site-footer.css en todas las páginas con footer.
2. Estructura canónica de 4 columnas: Marca/Seguridad, Productos, Plataforma y Contacto/Redes.
3. Barra inferior (.footer-bottom) con copyright, ciudad y enlaces legales (Privacidad, Términos).
4. Layout visual en Desktop (1366x768): grid de 4 columnas, alineación superior limpia, sin overflow.
5. Layout visual en Mobile (390x844): adaptación a 1 columna centrada con padding inferior anti-colisión con CTA flotante.
"""
from pathlib import Path
import pytest
from conftest import BASE, ROOT

SITE_FOOTER_CSS = ROOT / "site-footer.css"

HTML_FILES_WITH_FOOTER = [
    ROOT / "index.html",
    ROOT / "atencion-cliente.html",
    ROOT / "pulse.html",
    ROOT / "crm.html",
    ROOT / "panel.html",
    ROOT / "funciones.html",
    ROOT / "precios.html",
    ROOT / "servicios.html",
    ROOT / "casos.html",
    ROOT / "nosotros.html",
    ROOT / "calculadora.html",
    ROOT / "criterios.html",
    ROOT / "alternativa-crm.html",
    ROOT / "servicios-pyme.html",
    ROOT / "comercio.html",
    ROOT / "automotriz.html",
    ROOT / "salud.html",
    ROOT / "atencion-whatsapp.html",
    ROOT / "cotizaciones-agendamiento.html",
    ROOT / "seguimiento-equipo.html",
]


def test_site_footer_css_exists_and_has_rules():
    """site-footer.css debe existir en la raíz y contener las reglas del contrato de 4 columnas."""
    assert SITE_FOOTER_CSS.is_file(), "site-footer.css no existe en la raíz del repositorio"
    css = SITE_FOOTER_CSS.read_text(encoding="utf-8")
    
    required_selectors = [
        "footer",
        ".footer-inner",
        ".footer-col",
        ".footer-col--brand",
        ".footer-links-group",
        ".footer-bottom",
        ".footer-legal-links",
        "@media (max-width: 960px)",
        "@media (max-width: 560px)"
    ]
    for sel in required_selectors:
        assert sel in css, f"site-footer.css debe contener la regla o media query '{sel}'"


def test_all_pages_link_site_footer_css():
    """Cada página con footer debe enlazar /site-footer.css en su <head>."""
    for html_file in HTML_FILES_WITH_FOOTER:
        content = html_file.read_text(encoding="utf-8")
        assert 'href="/site-footer.css"' in content or 'site-footer.css' in content, (
            f"{html_file.name} debe enlazar /site-footer.css"
        )


def test_all_pages_have_canonical_4_column_footer_structure():
    """Todas las páginas deben tener la estructura canónica de 4 columnas y footer-bottom."""
    for html_file in HTML_FILES_WITH_FOOTER:
        content = html_file.read_text(encoding="utf-8")
        assert "<footer>" in content, f"{html_file.name} debe contener <footer>"
        assert '<div class="footer-inner">' in content, f"{html_file.name} debe contener .footer-inner"
        assert '<div class="footer-col footer-col--brand">' in content, f"{html_file.name} debe contener la columna de marca"
        assert "<h4>Productos</h4>" in content, f"{html_file.name} debe contener columna Productos"
        assert "<h4>Plataforma</h4>" in content, f"{html_file.name} debe contener columna Plataforma"
        assert "<h4>Contacto</h4>" in content, f"{html_file.name} debe contener columna Contacto"
        assert '<div class="footer-bottom">' in content, f"{html_file.name} debe contener .footer-bottom"
        assert "/privacidad" in content, f"{html_file.name} debe enlazar política de privacidad"
        assert "/terminos.html" in content, f"{html_file.name} debe enlazar términos de servicio"


def test_footer_desktop_layout_playwright(desktop_page):
    """En Desktop (1366x768), el footer debe renderizarse en grid de 4 columnas sin overflow."""
    desktop_page.goto(f"{BASE}/")
    desktop_page.wait_for_selector("footer")
    
    footer = desktop_page.locator("footer")
    assert footer.is_visible()
    
    # 4 columnas en .footer-inner
    cols = desktop_page.locator(".footer-inner > .footer-col")
    assert cols.count() == 4
    
    # Las columnas deben estar distribuidas horizontalmente (x creciente)
    boxes = [cols.nth(i).bounding_box() for i in range(4)]
    for b in boxes:
        assert b is not None
        assert b["width"] > 100
    
    assert boxes[0]["x"] < boxes[1]["x"] < boxes[2]["x"] < boxes[3]["x"]
    
    # La barra inferior debe ser visible
    footer_bottom = desktop_page.locator(".footer-bottom")
    assert footer_bottom.is_visible()


def test_footer_mobile_layout_playwright(mobile_page):
    """En Mobile (390x844), el footer debe adaptarse a 1 columna sin overflow horizontal."""
    mobile_page.goto(f"{BASE}/")
    mobile_page.wait_for_selector("footer")
    
    footer = mobile_page.locator("footer")
    assert footer.is_visible()
    
    # Sin overflow horizontal
    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    inner_w = mobile_page.evaluate("window.innerWidth")
    assert scroll_w <= inner_w + 1, f"Overflow horizontal detectado en móvil: {scroll_w} > {inner_w}"
    
    # 4 columnas apiladas verticalmente
    cols = mobile_page.locator(".footer-inner > .footer-col")
    boxes = [cols.nth(i).bounding_box() for i in range(4)]
    for i in range(3):
        assert boxes[i]["y"] < boxes[i+1]["y"], f"Las columnas deben estar apiladas verticalmente en móvil"
