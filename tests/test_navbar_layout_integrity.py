from pathlib import Path
import pytest
from playwright.sync_api import Page, expect

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED = {"404.html", "plataforma.html"}
HTML_PAGES = sorted([
    f"/{f.name}" for f in ROOT.glob("*.html")
    if not f.name.startswith("google") and f.name not in EXCLUDED
])

@pytest.mark.parametrize("page_path", HTML_PAGES)
def test_navbar_single_row_layout_desktop(page: Page, site_server: str, page_path: str):
    """Verifica mecánicamente que el navbar esté en una sola fila horizontal (sin wrapping) en todas las páginas."""
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{site_server}{page_path}", wait_until="domcontentloaded")
    
    header = page.locator("nav.site-header, .site-header").first
    expect(header).to_be_visible()
    
    header_box = header.bounding_box()
    assert header_box is not None
    # El navbar debe ser una barra horizontal delgada (~80px a 145px), nunca una caja colapsada de 300px+
    assert header_box["height"] < 160, f"Navbar demasiado alto ({header_box['height']}px) en {page_path}, indica wrapping vertical"
    
    logo = page.locator("nav.site-header .logo, .site-header .logo").first
    nav_links = page.locator("nav.site-header .site-nav, .site-header .site-nav").first
    menu_toggle = page.locator("nav.site-header .menu-toggle, .site-header .menu-toggle").first
    
    # En desktop, el botón hamburguesa móvil .menu-toggle debe estar estrictamente oculto (evita puntos/artefactos residuales)
    if menu_toggle.count() > 0:
        expect(menu_toggle).to_be_hidden()
    
    if logo.count() > 0 and nav_links.count() > 0:
        logo_box = logo.bounding_box()
        nav_box = nav_links.bounding_box()
        assert logo_box is not None and nav_box is not None
        # En desktop, el menú de navegación debe estar a la derecha del logo
        assert nav_box["x"] >= logo_box["x"], f"El menú de navegación debe ubicarse a la derecha del logo en {page_path}"
        # Logo y Nav deben estar alineados en la misma franja vertical
        assert abs(nav_box["y"] - logo_box["y"]) < 60, f"Logo (y={logo_box['y']}) y Nav (y={nav_box['y']}) desalineados en {page_path}"

@pytest.mark.parametrize("page_path", ["/index.html", "/facil.html", "/confianza.html", "/orquestacion.html"])
def test_navbar_mobile_toggle_layout(page: Page, site_server: str, page_path: str):
    """Verifica que en móvil el navbar se adapte limpiamente con el botón de menú visible."""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{site_server}{page_path}", wait_until="domcontentloaded")
    
    header = page.locator("nav.site-header, .site-header").first
    expect(header).to_be_visible()
    
    header_box = header.bounding_box()
    assert header_box is not None
    assert header_box["height"] < 130, f"Navbar móvil demasiado alto en {page_path}"


@pytest.mark.parametrize("page_path", HTML_PAGES)
def test_hero_content_and_badges_not_overlapped_by_navbar(page: Page, site_server: str, page_path: str):
    """Verifica que ningún elemento de contenido inicial (badge, pill o h1) quede tapado o solapado por el navbar fijo."""
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{site_server}{page_path}", wait_until="domcontentloaded")
    
    header = page.locator("nav.site-header, .site-header").first
    if header.count() == 0 or not header.is_visible():
        return

    header_box = header.bounding_box()
    assert header_box is not None
    header_bottom = header_box["y"] + header_box["height"]
    
    # 1. Verificar primer elemento de contenido visible en main o sección inicial
    first_target = page.locator(
        "main .dash-badge, section.hero .dash-badge, .hero-vertical .dash-badge, "
        "section:first-of-type .dash-badge, section:first-of-type .badge, "
        "main h1, section.hero h1, .hero-vertical h1, h1"
    ).first
    
    if first_target.count() > 0 and first_target.is_visible():
        target_box = first_target.bounding_box()
        assert target_box is not None
        assert target_box["y"] >= header_bottom + 15, (
            f"Elemento inicial '{first_target.text_content()[:40]}' en {page_path} está solapado por el navbar! "
            f"Navbar llega hasta y={header_bottom:.1f}px pero el elemento comienza en y={target_box['y']:.1f}px "
            f"(clearance={target_box['y'] - header_bottom:.1f}px, mínimo exigido 15px)"
        )

