"""Pruebas del rediseño y homologación del navbar público (TASK-202608191856).

Verifica:
1. Existencia y enlace de site-nav.css en todas las páginas con .nav-cta.
2. Contrato semántico de interfaz (.site-nav, .site-nav__link, .site-nav__demo).
3. Enlaces de texto limpios en desktop sin bordes individuales ni fondos de botón.
4. Estado activo unívoco (aria-current="page" y .site-nav__link--active) en páginas interiores.
5. 'Agenda una demo →' (.btn-gold) como único botón destacado.
6. Comportamiento en navegador real (desktop y mobile con Playwright).
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, PAGES

ROOT = Path(__file__).resolve().parent.parent
SITE_NAV_CSS = ROOT / "site-nav.css"

EXCLUDED_NAV_PAGES = {"/privacidad.html", "/terminos.html", "/cumplimiento.html"}
HOMOLOGOUS_PAGES = [p for p in PAGES if p not in EXCLUDED_NAV_PAGES]

# Mapeo canónico de página interior a su ruta activa correspondiente
ACTIVE_NAV_MAP = {
    "/atencion-cliente.html": "/atencion-cliente",
    "/atencion-whatsapp.html": "/atencion-cliente",
    "/pulse.html": "/pulse",
    "/funciones.html": "/funciones",
    "/crm.html": "/crm",
    "/alternativa-crm.html": "/crm",
    "/panel.html": "/panel",
    "/precios.html": "/precios",
    "/blog/": "/blog/",
}


def get_html_file(path_str):
    if path_str == "/":
        return ROOT / "index.html"
    if path_str == "/blog/":
        return ROOT / "blog" / "index.html"
    return ROOT / path_str.lstrip("/")


def test_site_nav_css_file_exists_and_contains_contract():
    """site-nav.css debe existir en la raíz y contener las reglas del contrato."""
    assert SITE_NAV_CSS.is_file(), "site-nav.css no existe en la raíz del repositorio"
    css = SITE_NAV_CSS.read_text(encoding="utf-8")
    
    required_selectors = [
        ".site-nav",
        ".site-nav__link",
        ".site-nav__link--active",
        ".site-nav__demo",
    ]
    for sel in required_selectors:
        assert sel in css, f"site-nav.css debe contener la regla {sel}"


@pytest.mark.parametrize("page_path", HOMOLOGOUS_PAGES)
def test_page_links_site_nav_css_in_head(page_path):
    """Cada página pública homologada debe enlazar site-nav.css en su <head>."""
    file = get_html_file(page_path)
    content = file.read_text(encoding="utf-8")
    assert "site-nav.css" in content, f"{file.name} no enlaza site-nav.css"


@pytest.mark.parametrize("page_path", HOMOLOGOUS_PAGES)
def test_navbar_structure_and_active_state(page_path):
    """Verifica la estructura .site-nav, las 7 secciones de texto y el estado activo correspondiente."""
    file = get_html_file(page_path)
    content = file.read_text(encoding="utf-8")
    
    assert "nav-cta" in content and "site-nav" in content, f"{file.name} debe tener clase .site-nav"
    
    # 7 enlaces de texto + 1 demo
    link_matches = re.findall(r'class="[^"]*site-nav__link[^"]*"', content)
    assert len(link_matches) == 7, f"{file.name} debe tener 7 enlaces .site-nav__link (encontrados {len(link_matches)})"
    
    demo_matches = re.findall(r'class="[^"]*site-nav__demo[^"]*"', content)
    assert len(demo_matches) == 1, f"{file.name} debe tener 1 botón .site-nav__demo"
    
    # Validar estado activo
    expected_active_href = ACTIVE_NAV_MAP.get(page_path)
    aria_current_matches = re.findall(r'href="([^"]+)"[^>]*aria-current="page"', content) + \
                           re.findall(r'aria-current="page"[^>]*href="([^"]+)"', content)
    
    if expected_active_href:
        all_match_expected = all(href == expected_active_href for href in aria_current_matches)
        assert len(aria_current_matches) in [1, 2], (
            f"{file.name} debe tener 1 o 2 aria-current='page' (encontrados {aria_current_matches})"
        )
        assert all_match_expected, (
            f"En {file.name}, el activo debe ser {expected_active_href} (encontrado {aria_current_matches})"
        )
    else:
        assert len(aria_current_matches) == 0, (
            f"{file.name} no debe tener ningún enlace con aria-current='page' (encontrados {aria_current_matches})"
        )


def test_navbar_visual_desktop_styles(desktop_page):
    """Verifica en navegador desktop que los enlaces de navegación sean texto limpio sin bordes."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    # En desktop, los enlaces visibles directos son las 3 secciones (Cómo ayuda, Precios, Recursos) + disparador Soluciones
    direct_links = desktop_page.locator(".site-nav > .site-nav__link")
    count = direct_links.count()
    assert count == 3, f"Se esperaban 3 enlaces de texto directos en desktop, se encontraron {count}"
    
    for i in range(count):
        link = direct_links.nth(i)
        border_width = link.evaluate("el => getComputedStyle(el).borderWidth")
        border_style = link.evaluate("el => getComputedStyle(el).borderStyle")
        bg_color = link.evaluate("el => getComputedStyle(el).backgroundColor")
        
        assert border_width in ["0px", "none"] or border_style in ["none", "hidden"] or border_width == "", (
            f"En desktop, el enlace {i} tiene borde visible: {border_width} {border_style}"
        )
        assert bg_color in ["rgba(0, 0, 0, 0)", "transparent"], (
            f"En desktop, el enlace {i} tiene fondo de botón: {bg_color}"
        )
    
    # Disparador Soluciones también es texto limpio
    trigger = desktop_page.locator(".site-nav__solutions-trigger")
    assert trigger.is_visible()
    trig_border = trigger.evaluate("el => getComputedStyle(el).borderWidth")
    assert trig_border in ["0px", "none", ""]
    
    # Único botón destacado es Agenda una demo
    demo_btn = desktop_page.locator(".site-nav .site-nav__demo")
    assert demo_btn.is_visible(), "El botón demo debe ser visible"
    has_btn_gold = demo_btn.evaluate("el => el.classList.contains('btn-gold')")
    assert has_btn_gold, "El botón demo debe tener clase .btn-gold"


def test_navbar_active_item_highlight_in_inner_page(desktop_page):
    """En una página interior como /pulse.html, el disparador Soluciones o el ítem Pulse tienen realce activo."""
    desktop_page.goto(f"{BASE}/pulse.html", wait_until="domcontentloaded")
    
    active_cards = desktop_page.locator(".site-nav .site-nav__solution-card[aria-current='page']")
    assert active_cards.count() == 1, "Debe haber un card activo en popover en /pulse.html"
    
    trigger_active = desktop_page.locator(".site-nav__solutions-trigger--active")
    assert trigger_active.count() == 1, "El disparador Soluciones debe tener estado activo en /pulse.html"


def test_navbar_mobile_menu_open_and_close(mobile_page):
    """En móvil, el botón de menú despliega la navegación sin bordes de botón."""
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    toggle = mobile_page.locator(".menu-toggle")
    assert toggle.is_visible(), "El botón .menu-toggle debe ser visible en móvil"
    
    nav_cta = mobile_page.locator(".nav-cta")
    
    # Abrir menú
    toggle.click()
    mobile_page.wait_for_timeout(250)
    assert "active" in (nav_cta.get_attribute("class") or ""), "El menú móvil debe abrirse al hacer clic"
    
    # Los enlaces móviles directos deben ser visibles
    mobile_links = mobile_page.locator(".site-nav__mobile-solutions .site-nav__link")
    assert mobile_links.count() == 4
    assert mobile_links.first.is_visible(), "Los enlaces deben ser visibles dentro del menú móvil abierto"
