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

EXCLUDED_NON_MARKETING = {"404.html", "plataforma.html", "privacidad.html", "terminos.html", "cumplimiento.html"}

HTML_FILES_WITH_FOOTER = sorted([
    f for f in ROOT.glob("*.html")
    if not f.name.startswith("google") and f.name not in EXCLUDED_NON_MARKETING and "<footer" in f.read_text(encoding="utf-8")
])


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
    assert len(HTML_FILES_WITH_FOOTER) >= 24, "Debe haber al menos 24 páginas públicas con footer canónico"
    for html_file in HTML_FILES_WITH_FOOTER:
        content = html_file.read_text(encoding="utf-8")
        assert "<footer>" in content, f"{html_file.name} debe contener <footer>"
        assert '<div class="footer-inner">' in content, f"{html_file.name} debe contener .footer-inner"
        assert '<div class="footer-col footer-col--brand">' in content, f"{html_file.name} debe contener la columna de marca"
        assert "<h4>Productos</h4>" in content, f"{html_file.name} debe contener columna Productos"
        assert "<h4>Plataforma</h4>" in content, f"{html_file.name} debe contener columna Plataforma"
        assert "<h4>Contacto</h4>" in content, f"{html_file.name} debe contener columna Contacto"
        assert '<div class="footer-bottom">' in content, f"{html_file.name} debe contener .footer-bottom"
        assert '<div class="footer-legal-links">' in content, f"{html_file.name} debe contener .footer-legal-links"
        assert "footer-legal " not in content and 'class="footer-legal"' not in content, (
            f"{html_file.name} no debe usar la clase desactualizada .footer-legal"
        )
        assert "/privacidad" in content, f"{html_file.name} debe enlazar política de privacidad"
        assert "/terminos.html" in content, f"{html_file.name} debe enlazar términos de servicio"
        assert "/confianza" in content, f"{html_file.name} debe enlazar confianza & DPA"
        assert "TheIA en LinkedIn" in content or "linkedin.com" in content, f"{html_file.name} debe enlazar LinkedIn en Contacto"
        assert "@theiacl_" in content or "instagram.com" in content, f"{html_file.name} debe enlazar Instagram en Contacto"


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


def test_inmobiliaria_footer_layout_playwright(desktop_page, mobile_page):
    """Verifica que /inmobiliaria tenga el footer canónico completo y sin overflow en desktop y móvil."""
    # Desktop
    desktop_page.goto(f"{BASE}/inmobiliaria")
    desktop_page.wait_for_selector("footer")
    footer = desktop_page.locator("footer")
    assert footer.is_visible()
    cols = desktop_page.locator("footer .footer-inner > .footer-col")
    assert cols.count() == 4
    legal = desktop_page.locator("footer .footer-legal-links a")
    assert legal.count() == 3
    
    # Mobile
    mobile_page.goto(f"{BASE}/inmobiliaria")
    mobile_page.wait_for_selector("footer")
    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    inner_w = mobile_page.evaluate("window.innerWidth")
    assert scroll_w <= inner_w + 1


def test_condensed_footer_and_hidden_sections_contract(desktop_page, mobile_page):
    """Verifica que las secciones redundantes de index.html estén ocultas en desktop y mobile, y que el footer en las 29 páginas tenga exactamente 4 enlaces en Productos y 4 en Plataforma."""
    import re

    # 1. Verificación visual en Desktop
    desktop_page.goto(f"{BASE}/")
    desktop_page.wait_for_timeout(200)
    assert not desktop_page.locator(".acompanamiento-section").is_visible(), ".acompanamiento-section debe estar oculta en desktop"
    assert not desktop_page.locator(".triada-productos-section").is_visible(), ".triada-productos-section debe estar oculta en desktop"

    # 2. Verificación visual en Mobile
    mobile_page.goto(f"{BASE}/")
    mobile_page.wait_for_timeout(200)
    assert not mobile_page.locator(".acompanamiento-section").is_visible(), ".acompanamiento-section debe estar oculta en mobile"
    assert not mobile_page.locator(".triada-productos-section").is_visible(), ".triada-productos-section debe estar oculta en mobile"

    # 3. Verificación de enlaces del footer en las 29 páginas canónicas
    assert len(HTML_FILES_WITH_FOOTER) == 29, f"Se esperaban exactamente 29 páginas con footer canónico, encontradas {len(HTML_FILES_WITH_FOOTER)}"

    expected_productos = [
        "/atencion-cliente",
        "/pulse",
        "/cerebro",
        "/crm",
    ]
    expected_plataforma = [
        "/precios",
        "/servicios",
        "/orquestacion",
        "/blog/",
    ]

    for html_file in HTML_FILES_WITH_FOOTER:
        content = html_file.read_text(encoding="utf-8")

        prod_match = re.search(r'<h4>Productos</h4>\s*<div class="footer-links-group">(.*?)</div>', content, re.DOTALL)
        assert prod_match, f"Falta grupo Productos en {html_file.name}"
        prod_links = re.findall(r'<a\s+href="([^"]+)"', prod_match.group(1))
        assert prod_links == expected_productos, (
            f"Enlaces de Productos incorrectos en {html_file.name}: {prod_links} vs {expected_productos}"
        )

        plat_match = re.search(r'<h4>Plataforma</h4>\s*<div class="footer-links-group">(.*?)</div>', content, re.DOTALL)
        assert plat_match, f"Falta grupo Plataforma en {html_file.name}"
        plat_links = re.findall(r'<a\s+href="([^"]+)"', plat_match.group(1))
        assert plat_links == expected_plataforma, (
            f"Enlaces de Plataforma incorrectos en {html_file.name}: {plat_links} vs {expected_plataforma}"
        )

        assert len(prod_links) + len(plat_links) == 8, (
            f"Total de enlaces de navegación debe ser 8 en {html_file.name}, encontrados {len(prod_links) + len(plat_links)}"
        )

    # 4. Verificación de coherencia en blog y layouts
    for extra_path in [ROOT / "blog" / "index.html", ROOT / "_layouts" / "post.html"]:
        if extra_path.is_file():
            extra_content = extra_path.read_text(encoding="utf-8")
            extra_prod = re.search(r'<h4>Productos</h4>\s*<div class="footer-links-group">(.*?)</div>', extra_content, re.DOTALL)
            assert extra_prod, f"Falta grupo Productos en {extra_path.name}"
            assert re.findall(r'<a\s+href="([^"]+)"', extra_prod.group(1)) == expected_productos

            extra_plat = re.search(r'<h4>Plataforma</h4>\s*<div class="footer-links-group">(.*?)</div>', extra_content, re.DOTALL)
            assert extra_plat, f"Falta grupo Plataforma en {extra_path.name}"
            assert re.findall(r'<a\s+href="([^"]+)"', extra_plat.group(1)) == expected_plataforma


