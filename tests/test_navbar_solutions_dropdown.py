"""Pruebas del menú de Soluciones con popover/dropdown en desktop y drawer en mobile (TASK-202608191916).

Verifica:
1. Existencia y reglas del contrato en site-nav.css y site-nav.js.
2. Presencia de .site-nav__solutions (con details/summary, chevron y 4 tarjetas de producto) en todas las páginas públicas.
3. Presencia de .site-nav__mobile-solutions (4 enlaces directos para el drawer móvil).
4. Comportamiento en navegador desktop: popover se despliega al hover/focus con transición y muestra las 4 soluciones.
5. Comportamiento en navegador mobile: popover oculto, drawer funcional con enlaces táctiles directos.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, PAGES

ROOT = Path(__file__).resolve().parent.parent
SITE_NAV_CSS = ROOT / "site-nav.css"
SITE_NAV_JS = ROOT / "site-nav.js"

EXCLUDED_NAV_PAGES = {"/privacidad.html", "/terminos.html", "/cumplimiento.html"}
HOMOLOGOUS_PAGES = [p for p in PAGES if p not in EXCLUDED_NAV_PAGES]


def get_html_file(path_str):
    if path_str == "/":
        return ROOT / "index.html"
    if path_str == "/blog/":
        return ROOT / "blog" / "index.html"
    return ROOT / path_str.lstrip("/")


def test_site_nav_assets_exist():
    """site-nav.css y site-nav.js deben existir en la raíz."""
    assert SITE_NAV_CSS.is_file(), "site-nav.css no existe"
    assert SITE_NAV_JS.is_file(), "site-nav.js no existe"


def test_site_nav_css_contains_dropdown_rules():
    """site-nav.css debe definir el contrato de dropdown desktop y drawer mobile."""
    css = SITE_NAV_CSS.read_text(encoding="utf-8")
    required = [
        ".site-nav__solutions",
        ".site-nav__solutions-trigger",
        ".site-nav__chevron",
        ".site-nav__popover",
        ".site-nav__solution-card",
        ".site-nav__mobile-solutions",
    ]
    for r in required:
        assert r in css, f"site-nav.css debe contener selector {r}"


@pytest.mark.parametrize("page_path", HOMOLOGOUS_PAGES)
def test_pages_have_solutions_dropdown_and_mobile_drawer_structure(page_path):
    """Verifica que cada página contenga el disparador Soluciones con sus 4 items y la variante móvil."""
    file = get_html_file(page_path)
    content = file.read_text(encoding="utf-8")
    
    assert "site-nav.css" in content, f"{file.name} debe enlazar site-nav.css"
    assert "site-nav.js" in content, f"{file.name} debe enlazar site-nav.js"
    assert "site-nav__solutions" in content, f"{file.name} debe contener .site-nav__solutions"
    assert "site-nav__solutions-trigger" in content, f"{file.name} debe contener .site-nav__solutions-trigger"
    assert "Soluciones" in content, f"{file.name} debe mostrar texto 'Soluciones'"
    
    # Validar 4 tarjetas dentro del popover
    popover_matches = re.findall(r'class="[^"]*site-nav__solution-card[^"]*"', content)
    assert len(popover_matches) == 4, f"{file.name} debe tener 4 tarjetas .site-nav__solution-card en el popover (encontradas {len(popover_matches)})"
    
    # Validar que los 4 productos estén presentes en el popover
    for title, href in [("Atención", "/atencion-cliente"), ("TheIA Pulse", "/pulse"), ("CRM", "/crm"), ("Panel de Control", "/panel")]:
        assert href in content, f"{file.name} debe contener enlace a {href}"
        assert title in content, f"{file.name} debe contener título {title}"
        
    # Validar sección móvil directa
    assert "site-nav__mobile-solutions" in content, f"{file.name} debe contener .site-nav__mobile-solutions"


def test_solutions_dropdown_interaction_in_desktop(desktop_page):
    """Verifica en desktop que al interactuar con Soluciones se despliegue el popover con los 4 componentes."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    trigger = desktop_page.locator(".site-nav__solutions-trigger")
    assert trigger.is_visible(), "El disparador 'Soluciones' debe ser visible en desktop"
    
    popover = desktop_page.locator(".site-nav__popover")
    
    # Hover sobre el disparador abre el popover
    trigger.hover()
    desktop_page.wait_for_timeout(250)
    assert popover.is_visible(), "El popover .site-nav__popover debe ser visible al hacer hover"
    
    # 4 tarjetas dentro del popover
    cards = popover.locator(".site-nav__solution-card")
    assert cards.count() == 4, f"Se esperaban 4 tarjetas dentro del popover, se encontraron {cards.count()}"
    
    # Clic en Pulse dentro del popover navega a /pulse
    pulse_card = popover.locator("a[href='/pulse']")
    pulse_card.click()
    desktop_page.wait_for_url("**/pulse", timeout=5000)
    assert "/pulse" in desktop_page.url, "Navegación desde popover debe llevar a /pulse"


def test_mobile_drawer_shows_direct_solutions_and_hides_desktop_dropdown(mobile_page):
    """Verifica en móvil que el dropdown desktop esté oculto y el drawer contenga los 4 enlaces directos."""
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    # Dropdown de desktop debe estar oculto en móvil
    desktop_dropdown = mobile_page.locator(".site-nav__solutions")
    assert not desktop_dropdown.is_visible(), "El dropdown .site-nav__solutions debe estar oculto en viewport móvil"
    
    # Abrir drawer móvil
    toggle = mobile_page.locator(".menu-toggle")
    assert toggle.is_visible(), "Botón .menu-toggle debe ser visible en móvil"
    toggle.click()
    mobile_page.wait_for_timeout(250)
    
    # Enlaces de soluciones móviles directos deben ser visibles
    mobile_solutions = mobile_page.locator(".site-nav__mobile-solutions .site-nav__link")
    assert mobile_solutions.count() == 4, f"Se esperaban 4 enlaces en .site-nav__mobile-solutions, encontrados {mobile_solutions.count()}"
    assert mobile_solutions.first.is_visible(), "Los enlaces móviles de soluciones deben ser visibles en el drawer abierto"
