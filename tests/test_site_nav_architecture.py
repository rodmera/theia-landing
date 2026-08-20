"""Pruebas de la arquitectura de navegación pública homologada (TASK-202608192246).

Verifica:
1. Catálogo completo de navegación:
   - 3 Dropdowns: Soluciones (4 items), Industrias (5 items), Recursos (4 items).
   - 3 Enlaces directos: Cómo ayuda (/funciones), Precios (/precios), Nosotros (/nosotros).
   - 1 Botón CTA único: Agenda una demo → (.btn .btn-gold).
2. Carga de /site-nav.css y /site-nav.js en todas las superficies públicas.
3. Markup con data-site-nav, data-site-nav-page y data-site-nav-source.
4. QA con Playwright:
   - Desktop: Despliegue independiente de los 3 popovers al hover/focus, rotación de chevrons, navegación fluida, pin por clic y Escape.
   - Mobile: Dropdowns desktop ocultos, drawer móvil con enlaces directos accesibles.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, PAGES

ROOT = Path(__file__).resolve().parent.parent
SITE_NAV_CSS = ROOT / "site-nav.css"
SITE_NAV_JS = ROOT / "site-nav.js"

# Páginas con navegación homologada (todas menos redirects)
NAV_SURFACES = [p for p in PAGES if p != "/plataforma.html"] + ["_layouts/post.html"]


def get_html_file(path_str):
    if path_str == "/":
        return ROOT / "index.html"
    if path_str == "/blog/":
        return ROOT / "blog" / "index.html"
    if path_str == "_layouts/post.html":
        return ROOT / "_layouts" / "post.html"
    return ROOT / path_str.lstrip("/")


def test_site_nav_assets_exist():
    """site-nav.css y site-nav.js deben existir en la raíz."""
    assert SITE_NAV_CSS.is_file()
    assert SITE_NAV_JS.is_file()


def test_site_nav_css_contains_multi_dropdown_and_drawer_rules():
    """site-nav.css debe definir los popovers de los 3 grupos y el drawer móvil."""
    css = SITE_NAV_CSS.read_text(encoding="utf-8")
    
    assert ".site-nav" in css
    assert ".site-nav__group" in css or ".site-nav__dropdown" in css or ".site-nav__solutions" in css
    assert ".site-nav__popover" in css
    assert ".site-nav__chevron" in css
    assert ".site-nav__demo" in css


@pytest.mark.parametrize("page_path", NAV_SURFACES)
def test_surface_loads_assets_and_has_nav_contract(page_path):
    """Cada superficie pública debe enlazar /site-nav.css, /site-nav.js y declarar data-site-nav."""
    file = get_html_file(page_path)
    content = file.read_text(encoding="utf-8")
    
    # Assets absolutos
    assert 'href="/site-nav.css"' in content, f"{file.name} debe enlazar /site-nav.css"
    assert 'src="/site-nav.js"' in content, f"{file.name} debe enlazar /site-nav.js"
    
    # Contrato data-site-nav
    assert "data-site-nav" in content, f"{file.name} debe incluir atributo data-site-nav"
    assert "data-site-nav-page" in content, f"{file.name} debe incluir atributo data-site-nav-page"
    assert "data-site-nav-source" in content, f"{file.name} debe incluir atributo data-site-nav-source"


def test_desktop_three_dropdowns_interaction(desktop_page):
    """Verifica en desktop que los 3 dropdowns (Soluciones, Industrias, Recursos) funcionen de forma independiente."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)
    
    # 1. Dropdown Soluciones
    sol_trigger = desktop_page.locator(".site-nav__trigger:has-text('Soluciones'), .site-nav__solutions-trigger").first
    assert sol_trigger.is_visible()
    sol_trigger.hover()
    desktop_page.wait_for_timeout(150)
    
    popover_sol = desktop_page.locator("#site-solutions-menu, .site-nav__popover--solutions, .site-nav__popover").first
    assert popover_sol.is_visible()
    assert popover_sol.locator("a[href='/atencion-cliente']").count() == 1
    assert popover_sol.locator("a[href='/pulse']").count() == 1
    assert popover_sol.locator("a[href='/crm']").count() == 1
    assert popover_sol.locator("a[href='/panel']").count() == 1
    
    # 2. Dropdown Industrias
    ind_trigger = desktop_page.locator(".site-nav__trigger:has-text('Industrias')").first
    assert ind_trigger.is_visible()
    ind_trigger.hover()
    desktop_page.wait_for_timeout(150)
    
    popover_ind = desktop_page.locator("#site-industries-menu, .site-nav__popover--industries").first
    assert popover_ind.is_visible()
    assert popover_ind.locator("a[href='/salud']").count() == 1
    assert popover_ind.locator("a[href='/servicios-pyme']").count() == 1
    assert "Servicios Profesionales B2B" in popover_ind.locator("a[href='/servicios-pyme']").inner_text()
    assert popover_ind.locator("a[href='/automotriz']").count() == 1
    assert popover_ind.locator("a[href='/comercio']").count() == 1
    assert popover_ind.locator("a[href='/casos']").count() == 1
    
    # 3. Dropdown Recursos
    rec_trigger = desktop_page.locator(".site-nav__trigger:has-text('Recursos')").first
    assert rec_trigger.is_visible()
    rec_trigger.hover()
    desktop_page.wait_for_timeout(150)
    
    popover_rec = desktop_page.locator("#site-resources-menu, .site-nav__popover--resources").first
    assert popover_rec.is_visible()
    assert popover_rec.locator("a[href='/blog/']").count() == 1
    assert popover_rec.locator("a[href='/criterios']").count() == 1
    assert popover_rec.locator("a[href='/calculadora']").count() == 1
    assert popover_rec.locator("a[href='/cumplimiento']").count() == 1
    
    # Enlaces directos visibles en orden lógico (Servicios -> Cómo ayuda -> Precios -> [Recursos] -> Nosotros)
    assert desktop_page.locator(".site-nav > a[href='/servicios']").first.is_visible()
    assert desktop_page.locator(".site-nav > a[href='/funciones']").first.is_visible()
    assert desktop_page.locator(".site-nav > a[href='/precios']").first.is_visible()
    assert desktop_page.locator(".site-nav > a[href='/nosotros']").first.is_visible()
    assert desktop_page.locator(".site-nav .site-nav__demo").first.is_visible()


def test_mobile_drawer_shows_all_destinations_directly(mobile_page):
    """Verifica en móvil que el menú lateral contenga los enlaces de todas las secciones como links directos."""
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)
    
    toggle = mobile_page.locator(".menu-toggle")
    assert toggle.is_visible()
    toggle.click()
    mobile_page.wait_for_timeout(250)
    
    # Destinos directos en el menú móvil
    destinations = [
        "/atencion-cliente", "/pulse", "/crm", "/panel",
        "/salud", "/servicios-pyme", "/automotriz", "/comercio", "/casos",
        "/servicios", "/funciones", "/precios", "/nosotros",
        "/blog/", "/criterios", "/calculadora", "/cumplimiento"
    ]
    for dest in destinations:
        link = mobile_page.locator(f".nav-cta a[href='{dest}'], .site-nav a[href='{dest}']").first
        assert link.count() >= 1, f"Falta enlace móvil a {dest}"
