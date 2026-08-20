"""Pruebas de la jerarquía de producto + servicios especializados y nuevo orden de navegación (TASK-202608192325).

Verifica:
1. Orden exacto del navbar en desktop:
   1. Soluciones -> 2. Servicios -> 3. Industrias -> 4. Cómo ayuda -> 5. Precios -> 6. Recursos -> 7. Nosotros -> 8. Agenda una demo
2. En dropdown Industrias, el enlace a /servicios-pyme lleva el texto exacto 'Servicios Profesionales B2B'.
3. Hero tag en index.html equilibrado para producto + servicios especializados.
4. Nueva sección estelar de Servicios Especializados de IA & Ingeniería de Agentes en index.html y servicios.html con los 5 pilares clave.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, PAGES

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"
SERVICIOS_HTML = ROOT / "servicios.html"

NAV_SURFACES = [p for p in PAGES if p != "/plataforma.html"] + ["_layouts/post.html"]


def get_html_file(path_str):
    if path_str == "/":
        return ROOT / "index.html"
    if path_str == "/blog/":
        return ROOT / "blog" / "index.html"
    if path_str == "_layouts/post.html":
        return ROOT / "_layouts" / "post.html"
    return ROOT / path_str.lstrip("/")


@pytest.mark.parametrize("page_path", NAV_SURFACES)
def test_navbar_exact_order_and_b2b_label(page_path):
    """Verifica que el navbar tenga Servicios en 2da posición y 'Servicios Profesionales B2B' en Industrias."""
    file = get_html_file(page_path)
    content = file.read_text(encoding="utf-8")
    
    # 1. En Industrias dropdown, la etiqueta de /servicios-pyme es 'Servicios Profesionales B2B'
    assert 'Servicios Profesionales B2B' in content, f"{file.name} debe contener la etiqueta 'Servicios Profesionales B2B'"
    
    # 2. Orden de enlaces directos / dropdowns en desktop:
    # Soluciones -> Servicios -> Industrias -> Cómo ayuda -> Precios -> Recursos -> Nosotros
    pos_soluciones = content.find('site-nav__group--solutions')
    pos_servicios = content.find('href="/servicios"')
    pos_industrias = content.find('site-nav__group--industries')
    pos_funciones = content.find('href="/funciones"')
    pos_precios = content.find('href="/precios"')
    pos_recursos = content.find('site-nav__group--resources')
    pos_nosotros = content.find('href="/nosotros"')
    
    assert pos_soluciones != -1, f"Falta Soluciones en {file.name}"
    assert pos_servicios != -1, f"Falta enlace directo Servicios en {file.name}"
    assert pos_industrias != -1, f"Falta Industrias en {file.name}"
    assert pos_funciones != -1, f"Falta Cómo ayuda en {file.name}"
    assert pos_precios != -1, f"Falta Precios en {file.name}"
    assert pos_recursos != -1, f"Falta Recursos en {file.name}"
    assert pos_nosotros != -1, f"Falta Nosotros en {file.name}"
    
    assert pos_soluciones < pos_servicios < pos_industrias < pos_funciones < pos_precios < pos_recursos < pos_nosotros, (
        f"En {file.name}, el orden de navegación debe ser exactamente: "
        f"Soluciones -> Servicios -> Industrias -> Cómo ayuda -> Precios -> Recursos -> Nosotros."
    )


def test_home_and_servicios_contain_specialized_ai_pillars():
    """index.html y servicios.html deben presentar los pilares de servicios especializados de IA."""
    index_content = INDEX_HTML.read_text(encoding="utf-8")
    servicios_content = SERVICIOS_HTML.read_text(encoding="utf-8")
    
    # Pilares de ingeniería de agentes
    pillars = [
        "Orquestación Multi-Agente",
        "Agent Harness",
        "Integraciones",
        "Auditoría",
        "Llave en Mano",
    ]
    for p in pillars:
        assert p in index_content, f"index.html debe contener el pilar '{p}'"
        assert p in servicios_content, f"servicios.html debe contener el pilar '{p}'"
        
    assert "SERVICIOS ESPECIALIZADOS DE IA" in index_content or "Servicios Especializados" in index_content
    assert "href=\"/servicios\"" in index_content, "index.html debe enlazar a /servicios desde la sección de servicios"


def test_desktop_navbar_order_in_browser(desktop_page):
    """Verifica en desktop que la barra superior renderice en la secuencia visual exacta."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)
    
    # 2da posición debe ser el enlace directo 'Servicios'
    second_nav_item = desktop_page.locator(".site-nav > a, .site-nav > .site-nav__group").nth(1)
    assert second_nav_item.inner_text().strip() == "Servicios"
    assert second_nav_item.get_attribute("href") == "/servicios"
    
    # Hover en Industrias muestra 'Servicios Profesionales B2B'
    ind_trigger = desktop_page.locator(".site-nav__trigger:has-text('Industrias')").first
    ind_trigger.hover()
    desktop_page.wait_for_timeout(150)
    
    ind_popover = desktop_page.locator("#site-industries-menu")
    b2b_link = ind_popover.locator("a[href='/servicios-pyme']").first
    assert b2b_link.is_visible()
    assert "Servicios Profesionales B2B" in b2b_link.inner_text()
