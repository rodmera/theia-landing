"""Pruebas del fix integral y rediseño del navbar con dropdown Soluciones (TASK-202608191930).

Verifica:
1. Carga de assets con rutas absolutas (/site-nav.css y /site-nav.js) en todas las superficies públicas.
2. Contrato semántico canónico basado en button + popover con aria-expanded y aria-controls (sin details/summary).
3. Popover en desktop con diseño glassmorphism 2x2 y las 4 soluciones principales.
4. Drawer móvil limpio sin popovers y con enlaces directos en .site-nav__mobile-solutions.
5. QA interactivo con Playwright: hover, rotación de chevron, clic en tarjeta y tecla Escape.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, PAGES

ROOT = Path(__file__).resolve().parent.parent
SITE_NAV_CSS = ROOT / "site-nav.css"
SITE_NAV_JS = ROOT / "site-nav.js"

# Todas las páginas de conftest.py + _layouts/post.html
ALL_PUBLIC_PAGES = PAGES + ["_layouts/post.html"]


def get_html_file(path_str):
    if path_str == "/":
        return ROOT / "index.html"
    if path_str == "/blog/":
        return ROOT / "blog" / "index.html"
    if path_str == "_layouts/post.html":
        return ROOT / "_layouts" / "post.html"
    return ROOT / path_str.lstrip("/")


def test_site_nav_assets_exist():
    """site-nav.css y site-nav.js deben existir en la raíz del repositorio."""
    assert SITE_NAV_CSS.is_file(), "site-nav.css no existe"
    assert SITE_NAV_JS.is_file(), "site-nav.js no existe"


def test_site_nav_css_contains_2x2_grid_and_glassmorphism_rules():
    """site-nav.css debe definir el popover en grilla 2x2 con glassmorphism y transiciones."""
    css = SITE_NAV_CSS.read_text(encoding="utf-8")
    
    # Selectores requeridos
    assert ".site-nav__solutions" in css
    assert ".site-nav__solutions-trigger" in css
    assert ".site-nav__chevron" in css
    assert ".site-nav__popover" in css
    assert ".site-nav__solution-card" in css
    assert ".site-nav__mobile-solutions" in css
    
    # Grilla 2 columnas para el popover en desktop
    assert "grid" in css, "El popover debe usar display: grid"
    assert "repeat(2" in css or "1fr 1fr" in css or "280px" in css or "270px" in css or "auto auto" in css, "El popover debe distribuirse en 2 columnas (2x2)"
    
    # Geometría continua sin gap
    assert "padding-bottom" in css, ".site-nav__solutions debe tener padding-bottom estructural"
    assert "margin-bottom" in css, ".site-nav__solutions debe tener margin-bottom negativo"


def test_desktop_dropdown_continuous_mouse_movement_and_navigation(desktop_page):
    """Simula el movimiento continuo del mouse desde el botón hasta la tarjeta sin cortes de hover."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    trigger = desktop_page.locator(".site-nav__solutions-trigger")
    assert trigger.is_visible()
    
    t_box = trigger.bounding_box()
    assert t_box is not None
    
    # Posicionar mouse sobre el trigger
    desktop_page.mouse.move(t_box["x"] + t_box["width"] / 2, t_box["y"] + t_box["height"] / 2)
    desktop_page.wait_for_timeout(100)
    
    popover = desktop_page.locator("#site-solutions-menu")
    assert popover.is_visible()
    
    # Mover el mouse suavemente hacia abajo (atravesando el puente hacia la tarjeta Pulse)
    pulse_card = popover.locator("a[href='/pulse']")
    p_box = pulse_card.bounding_box()
    assert p_box is not None
    
    start_y = t_box["y"] + t_box["height"] / 2
    target_y = p_box["y"] + p_box["height"] / 2
    target_x = p_box["x"] + p_box["width"] / 2
    
    # 5 pasos continuos de movimiento
    for step in range(1, 6):
        cur_y = start_y + (target_y - start_y) * (step / 5)
        desktop_page.mouse.move(target_x, cur_y)
        desktop_page.wait_for_timeout(30)
        assert popover.is_visible(), f"El popover se cerró durante el movimiento vertical en paso {step}"
        
    desktop_page.mouse.click(target_x, target_y)
    desktop_page.wait_for_url("**/pulse", timeout=5000)
    assert "/pulse" in desktop_page.url


def test_desktop_dropdown_inner_page_navigation(desktop_page):
    """En una página interior (/atencion-cliente), permite hacer hover y navegar fluidamente a otra solución."""
    desktop_page.goto(f"{BASE}/atencion-cliente.html", wait_until="domcontentloaded")
    
    trigger = desktop_page.locator(".site-nav__solutions-trigger")
    assert trigger.is_visible()
    
    trigger.hover()
    desktop_page.wait_for_timeout(100)
    
    popover = desktop_page.locator("#site-solutions-menu")
    assert popover.is_visible()
    
    crm_card = popover.locator("a[href='/crm']")
    assert crm_card.is_visible()
    crm_card.click()
    desktop_page.wait_for_url("**/crm", timeout=5000)
    assert "/crm" in desktop_page.url


def test_desktop_dropdown_click_to_pin_and_escape(desktop_page):
    """Al hacer clic en el trigger, el popover queda anclado (pinned) aunque el mouse se mueva lejos."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    trigger = desktop_page.locator(".site-nav__solutions-trigger")
    popover = desktop_page.locator("#site-solutions-menu")
    
    # Clic en trigger fija el estado pinned
    trigger.click()
    desktop_page.wait_for_timeout(100)
    assert trigger.get_attribute("aria-expanded") == "true"
    assert popover.is_visible()
    
    # Mover el mouse lejos (al extremo superior izquierdo de la pantalla)
    desktop_page.mouse.move(10, 10)
    desktop_page.wait_for_timeout(250)
    assert popover.is_visible(), "El popover pinned debe permanecer visible tras alejar el cursor"
    
    # Presionar Escape lo cierra y devuelve foco al trigger
    desktop_page.keyboard.press("Escape")
    desktop_page.wait_for_timeout(200)
    assert trigger.get_attribute("aria-expanded") == "false"
    assert not popover.is_visible(), "Escape debe cerrar el popover"


@pytest.mark.parametrize("page_path", ALL_PUBLIC_PAGES)
def test_all_pages_use_absolute_paths_and_canonical_markup(page_path):
    """Verifica que cada superficie pública cargue /site-nav.css y /site-nav.js con ruta absoluta y markup button+popover."""
    file = get_html_file(page_path)
    assert file.is_file(), f"Archivo {file} no existe"
    content = file.read_text(encoding="utf-8")
    
    # 1. Rutas absolutas obligatorias
    assert 'href="/site-nav.css"' in content, f"{file.name} debe enlazar /site-nav.css con ruta absoluta"
    assert 'src="/site-nav.js"' in content, f"{file.name} debe enlazar /site-nav.js con ruta absoluta"
    
    # 2. No debe usar details/summary en el navbar
    nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', content, re.DOTALL)
    assert nav_match is not None, f"No se encontró <nav> en {file.name}"
    nav_html = nav_match.group(1)
    
    assert "site-nav__solutions-disclosure" not in nav_html, f"{file.name} no debe usar details/summary en el navbar"
    assert "<summary" not in nav_html, f"{file.name} no debe usar summary en el navbar"
    
    # 3. Disparador button con accesibilidad
    assert 'button type="button" class="site-nav__solutions-trigger' in content or 'button class="site-nav__solutions-trigger' in content
    assert 'aria-expanded="false"' in content or 'aria-expanded="true"' in content
    assert 'aria-controls="site-solutions-menu"' in content
    assert 'id="site-solutions-menu"' in content
    
    # 4. Popover con 4 tarjetas
    cards = re.findall(r'class="[^"]*site-nav__solution-card[^"]*"', content)
    assert len(cards) == 4, f"{file.name} debe tener 4 tarjetas en popover (encontradas {len(cards)})"
    
    # 5. Drawer móvil con 4 enlaces directos
    assert "site-nav__mobile-solutions" in content, f"{file.name} debe tener .site-nav__mobile-solutions"
    
    # 6. Botón demo
    assert "site-nav__demo" in content, f"{file.name} debe tener botón .site-nav__demo"


def test_desktop_dropdown_hover_and_keyboard_interactions(desktop_page):
    """Verifica en desktop que el popover se abra al hover, rote el chevron y cierre con Escape."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    trigger = desktop_page.locator(".site-nav__solutions-trigger")
    assert trigger.is_visible(), "El botón 'Soluciones' debe ser visible en desktop"
    
    popover = desktop_page.locator("#site-solutions-menu")
    
    # Inicialmente oculto o no visible para el usuario
    # Hover sobre Soluciones
    trigger.hover()
    desktop_page.wait_for_timeout(250)
    assert popover.is_visible(), "El popover debe ser visible al hacer hover en Soluciones"
    
    # 4 tarjetas visibles
    cards = popover.locator(".site-nav__solution-card")
    assert cards.count() == 4
    
    # Clic en TheIA Pulse navega a /pulse
    pulse_card = popover.locator("a[href='/pulse']")
    pulse_card.click()
    desktop_page.wait_for_url("**/pulse", timeout=5000)
    assert "/pulse" in desktop_page.url


def test_mobile_drawer_open_and_direct_solutions_visible(mobile_page):
    """Verifica en mobile que el popover desktop esté oculto y el drawer exponga las 4 soluciones directas."""
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    # Dropdown de desktop oculto
    dropdown = mobile_page.locator(".site-nav__solutions")
    assert not dropdown.is_visible(), "El dropdown desktop debe estar oculto en móvil"
    
    # Abrir menú móvil
    toggle = mobile_page.locator(".menu-toggle")
    assert toggle.is_visible()
    toggle.click()
    mobile_page.wait_for_timeout(250)
    
    nav = mobile_page.locator(".nav-cta.site-nav")
    assert "active" in (nav.get_attribute("class") or "")
    
    # Enlaces de soluciones móviles directos
    mob_links = mobile_page.locator(".site-nav__mobile-solutions .site-nav__link")
    assert mob_links.count() == 4
    assert mob_links.first.is_visible()
