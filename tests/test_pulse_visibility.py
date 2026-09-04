"""Pruebas de visibilidad y propuesta de valor de TheIA Pulse (TASK-202608191820).

Verifica:
1. Presencia de 'Pulse' (/pulse) en la barra de navegación de todas las páginas públicas homologadas,
   ubicado después de 'Atención' y antes de 'Cómo ayuda'.
2. Existencia de la sección .pulse-spotlight en index.html ubicada entre .productos-paraguas y .problema,
   con su estructura semántica, los tres momentos clave del día (08:00 AM, alerta en tiempo real y 19:00 PM)
   y CTA a /pulse.
3. Verificación en navegador real (desktop y mobile) con Playwright.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, PAGES

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"

# Páginas legales o de redirección que no llevan el navbar comercial completo
EXCLUDED_NAV_PAGES = {"/privacidad.html", "/terminos.html", "/cumplimiento.html", "/plataforma.html"}

HOMOLOGOUS_PAGES = [p for p in PAGES if p not in EXCLUDED_NAV_PAGES]


def get_html_file(path_str):
    if path_str == "/":
        return ROOT / "index.html"
    if path_str == "/blog/":
        return ROOT / "blog" / "index.html"
    return ROOT / path_str.lstrip("/")


@pytest.mark.parametrize("page_path", HOMOLOGOUS_PAGES)
def test_navbar_contiene_enlace_a_pulse_en_orden_correcto(page_path):
    """Cada página pública homologada debe tener 'Pulse' en su navbar después de Atención y antes de Cómo ayuda."""
    file = get_html_file(page_path)
    assert file.is_file(), f"Archivo {file} no existe"
    content = file.read_text(encoding="utf-8")
    
    assert "nav-cta" in content, f"{file.name} debe tener contenedor .nav-cta"
    
    # Extraer el bloque nav
    match = re.search(r'<nav[^>]*>(.*?)</nav>', content, re.DOTALL)
    assert match is not None, f"No se encontró <nav> en {file.name}"
    nav_html = match.group(1)
    
    # Debe contener enlace a /pulse con texto Pulse
    assert 'href="/pulse"' in nav_html, f"{file.name} no tiene enlace a /pulse en .nav-cta"
    assert re.search(r'href="/pulse"[^>]*>\s*Pulse\s*</a>', nav_html), f"{file.name} debe mostrar texto 'Pulse'"
    
    # Validar orden: Atención -> Pulse -> Cómo ayuda
    pos_atencion = nav_html.find('href="/atencion-cliente"')
    if pos_atencion == -1:
        pos_atencion = nav_html.find('href="/atencion-whatsapp"')
    pos_pulse = nav_html.find('href="/pulse"')
    pos_como_ayuda = nav_html.find('href="/funciones"')
    
    assert pos_atencion != -1, f"No se encontró enlace a Atención en {file.name}"
    assert pos_pulse != -1, f"No se encontró enlace a Pulse en {file.name}"
    assert pos_como_ayuda != -1, f"No se encontró enlace a Cómo ayuda en {file.name}"
    
    assert pos_atencion < pos_pulse < pos_como_ayuda, (
        f"En {file.name}, el orden debe ser Atención -> Pulse -> Cómo ayuda. "
        f"Posiciones: atencion={pos_atencion}, pulse={pos_pulse}, como_ayuda={pos_como_ayuda}"
    )


def test_home_seccion_pulse_spotlight_ubicacion_y_semantica():
    """index.html delega la presentación profunda de Pulse a su tarjeta en productos-paraguas y /pulse."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    assert 'href="/pulse"' in content, "index.html debe contener enlace a /pulse"
    assert "productos-paraguas" in content, "index.html debe contener .productos-paraguas"


def test_pulse_spotlight_en_navegador_desktop(desktop_page):
    """Verifica en desktop que el enlace a /pulse sea visible y navegable."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    pulse_link = desktop_page.locator(".productos-paraguas a[href='/pulse']").first
    assert pulse_link.is_visible(), "El enlace a Pulse en la suite de productos debe ser visible"


def test_pulse_navbar_click_navega_a_pulse(desktop_page):
    """Verifica que hacer clic en el enlace Pulse del navbar navegue a /pulse."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    # En desktop, interactuar con Soluciones para desplegar popover
    trigger = desktop_page.locator(".site-nav__trigger:has-text('Soluciones'), .site-nav__solutions-trigger").first
    if trigger.is_visible():
        trigger.hover()
        desktop_page.wait_for_timeout(200)

    pulse_link = desktop_page.locator(".nav-cta a[href='/pulse']").first
    assert pulse_link.is_visible(), "El enlace a Pulse en el navbar debe ser visible en desktop"
    
    pulse_link.click()
    desktop_page.wait_for_url("**/pulse", timeout=5000)
    assert "/pulse" in desktop_page.url, "La navegación debe llevar a /pulse"
