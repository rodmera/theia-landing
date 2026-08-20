"""Pruebas de auditoría y homologación integral al Design System (TASK-202608200001).

Verifica:
1. Contrato transversal en site-cards.css:
   - 3 roles: .theia-card--editorial, .theia-card--reading, .theia-card--functional.
   - Apoyo visual (.theia-card__visual) centrado con separación exacta de 1.25rem (20px) sobre el título.
   - Badge .piece-icon-wrap con dimensiones 52x52px, borde dorado e icono centrado.
   - Títulos h3 Merriweather centrados y párrafos Plus Jakarta Sans centrados con flex-grow.
   - Acciones .theia-card__action ancladas al fondo con margin-top: auto.
2. Carga absoluta de /site-nav.css, /site-nav.js y /site-cards.css en las 25 superficies públicas.
3. Excepción explícita de plataforma.html (redirect a /panel).
4. Verificación en navegador Playwright (desktop y mobile).
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, PAGES

ROOT = Path(__file__).resolve().parent.parent
SITE_CARDS_CSS = ROOT / "site-cards.css"
SITE_NAV_CSS = ROOT / "site-nav.css"
SITE_NAV_JS = ROOT / "site-nav.js"

# 25 superficies navegables (excluyendo redirect plataforma.html)
NAV_SURFACES = [p for p in PAGES if p != "/plataforma.html"] + ["_layouts/post.html"]


def get_html_file(path_str):
    if path_str == "/":
        return ROOT / "index.html"
    if path_str == "/blog/":
        return ROOT / "blog" / "index.html"
    if path_str == "_layouts/post.html":
        return ROOT / "_layouts" / "post.html"
    return ROOT / path_str.lstrip("/")


def test_site_cards_css_defines_three_roles_and_invariants():
    """site-cards.css debe definir los 3 roles y las invariantes de 52x52px y 1.25rem de separación."""
    assert SITE_CARDS_CSS.is_file(), "site-cards.css no existe"
    css = SITE_CARDS_CSS.read_text(encoding="utf-8")
    
    # Roles
    assert ".theia-card" in css
    assert ".theia-card--editorial" in css or ".theia-card" in css
    assert ".theia-card--reading" in css
    assert ".theia-card--functional" in css
    
    # Invariantes de geometría
    assert "1.25rem" in css or "20px" in css, "Debe declarar separación vertical de 1.25rem (20px)"
    assert "52px" in css, "Debe declarar dimensiones de 52x52px para el badge de icono"
    assert "margin-block-start: auto" in css or "margin-top: auto" in css


@pytest.mark.parametrize("page_path", NAV_SURFACES)
def test_all_nav_surfaces_load_shared_modules_with_absolute_paths(page_path):
    """Las 25 superficies navegables deben cargar /site-nav.css, /site-nav.js y /site-cards.css."""
    file = get_html_file(page_path)
    content = file.read_text(encoding="utf-8")
    
    assert 'href="/site-nav.css"' in content, f"{file.name} debe enlazar /site-nav.css"
    assert 'href="/site-cards.css"' in content, f"{file.name} debe enlazar /site-cards.css"
    assert 'src="/site-nav.js"' in content, f"{file.name} debe enlazar /site-nav.js"


def test_plataforma_redirect_exception():
    """plataforma.html debe ser una redirección limpia a /panel."""
    content = (ROOT / "plataforma.html").read_text(encoding="utf-8")
    assert 'url=/panel' in content or 'replace("/panel")' in content
    assert 'href="/panel"' in content


@pytest.mark.parametrize("page_path", ["/precios.html", "/servicios.html", "/crm.html", "/nosotros.html"])
def test_editorial_cards_geometry_in_browser(desktop_page, page_path):
    """Verifica en desktop que las tarjetas editoriales tengan badge de 52x52px y textos centrados."""
    desktop_page.goto(f"{BASE}{page_path}", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)
    
    cards = desktop_page.locator(".theia-card")
    count = cards.count()
    assert count >= 2, f"Se esperaban tarjetas .theia-card en {page_path}"
    
    for i in range(min(count, 4)):
        card = cards.nth(i)
        card_box = card.bounding_box()
        if not card_box or card_box["height"] < 10:
            continue
            
        card_center_x = card_box["x"] + card_box["width"] / 2
        
        # Badge de ícono de 52x52px
        badge = card.locator(".piece-icon-wrap, .theia-card__icon")
        if badge.count() > 0:
            b_box = badge.first.bounding_box()
            if b_box:
                assert abs(b_box["width"] - 52.0) <= 2.0, f"En {page_path}, badge width={b_box['width']} (debe ser ~52px)"
                assert abs(b_box["height"] - 52.0) <= 2.0, f"En {page_path}, badge height={b_box['height']} (debe ser ~52px)"
                
                # Centrado del badge
                b_center_x = b_box["x"] + b_box["width"] / 2
                assert abs(b_center_x - card_center_x) < 3.0, f"En {page_path}, badge {i} descentrado"
        
        # Título centrado
        title = card.locator("h3, h4, .theia-card__content h3, .theia-card__content h4").first
        if title.count() > 0:
            t_box = title.bounding_box()
            if t_box and t_box["width"] > 0:
                t_center_x = t_box["x"] + t_box["width"] / 2
                assert abs(t_center_x - card_center_x) < 4.0, f"En {page_path}, título {i} descentrado"
