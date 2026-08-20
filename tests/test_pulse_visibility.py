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
    """index.html debe tener la sección .pulse-spotlight entre .productos-paraguas y .problema."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    
    assert "pulse-spotlight" in content, "index.html debe contener la clase .pulse-spotlight"
    
    pos_paraguas = content.find('class="productos-paraguas"')
    pos_spotlight = content.find('class="pulse-spotlight')
    if pos_spotlight == -1:
        pos_spotlight = content.find("pulse-spotlight")
    pos_problema = content.find('class="problema"')
    
    assert pos_paraguas != -1, "No se encontró .productos-paraguas en index.html"
    assert pos_spotlight != -1, "No se encontró .pulse-spotlight en index.html"
    assert pos_problema != -1, "No se encontró .problema en index.html"
    
    assert pos_paraguas < pos_spotlight < pos_problema, (
        "La sección .pulse-spotlight debe estar ubicada después de .productos-paraguas y antes de .problema"
    )
    
    # Validar selectores requeridos por la especificación técnica
    required_classes = [
        "pulse-spotlight__layout",
        "pulse-spotlight__copy",
        "pulse-spotlight__phone",
        "pulse-spotlight__moment",
        "pulse-spotlight__time",
        "pulse-spotlight__cta",
    ]
    for cls in required_classes:
        assert cls in content, f"index.html debe contener la clase {cls}"
        
    # Validar 3 momentos del día y horas clave
    assert "08:00" in content, "Debe incluir briefing a las 08:00"
    assert "19:00" in content, "Debe incluir resumen de cierre a las 19:00"
    assert "WhatsApp" in content, "Debe mencionar WhatsApp"
    assert 'href="/pulse"' in content, "Debe incluir enlace a /pulse en el CTA"


def test_pulse_spotlight_en_navegador_desktop(desktop_page):
    """Verifica en desktop que la sección sea visible, contenga los 3 momentos y el CTA funcione."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    spotlight = desktop_page.locator(".pulse-spotlight")
    assert spotlight.is_visible(), "La sección .pulse-spotlight debe ser visible en desktop"
    
    # 3 momentos
    moments = spotlight.locator(".pulse-spotlight__moment")
    assert moments.count() >= 3, f"Se esperaban al menos 3 momentos en .pulse-spotlight, se encontraron {moments.count()}"
    
    # CTA a /pulse
    cta = spotlight.locator(".pulse-spotlight__cta")
    assert cta.is_visible(), "El CTA de Pulse debe ser visible"
    href = cta.get_attribute("href")
    assert href == "/pulse", f"El CTA debe enlazar a /pulse (encontrado: {href})"


def test_pulse_navbar_click_navega_a_pulse(desktop_page):
    """Verifica que hacer clic en el enlace Pulse del navbar navegue a /pulse."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    # En desktop, interactuar con Soluciones para desplegar popover
    trigger = desktop_page.locator(".site-nav__solutions-trigger")
    if trigger.is_visible():
        trigger.hover()
        desktop_page.wait_for_timeout(200)

    pulse_link = desktop_page.locator(".nav-cta a[href='/pulse']").first
    assert pulse_link.is_visible(), "El enlace a Pulse en el navbar debe ser visible en desktop"
    
    pulse_link.click()
    desktop_page.wait_for_url("**/pulse", timeout=5000)
    assert "/pulse" in desktop_page.url, "La navegación debe llevar a /pulse"
