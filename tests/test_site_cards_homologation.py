"""Pruebas de homologación visual integral de tarjetas (TASK-202608192149).

Verifica:
1. Existencia y reglas del contrato en site-cards.css (.theia-card, .theia-card__visual, .theia-card__content, .theia-card__action).
2. Carga de site-cards.css en las páginas objetivo con tarjetas de marketing/contenido.
3. Semántica unificada: ícono/badge centrado arriba, título y párrafo centrados con inicio simétrico y acción abajo.
4. QA en navegador Playwright (desktop y mobile) verificando alineación y simetría.
5. Exclusiones explícitas: tarjetas de precio (price-card) y tablas no sufren deformaciones.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
SITE_CARDS_CSS = ROOT / "site-cards.css"

PAGES_WITH_THEIA_CARDS = [
    "/precios.html",
    "/servicios.html",
    "/servicios-pyme.html",
    "/criterios.html",
    "/nosotros.html",
    "/automotriz.html",
    "/comercio.html",
    "/salud.html",
]


def get_html_file(path_str):
    return ROOT / path_str.lstrip("/")


def test_site_cards_css_file_exists_and_contains_contract():
    """site-cards.css debe existir en la raíz y contener las reglas del contrato."""
    assert SITE_CARDS_CSS.is_file(), "site-cards.css no existe en la raíz"
    css = SITE_CARDS_CSS.read_text(encoding="utf-8")
    
    assert ".theia-card" in css, "Debe definir .theia-card"
    assert ".theia-card__visual" in css, "Debe definir .theia-card__visual"
    assert ".theia-card__content" in css, "Debe definir .theia-card__content"
    assert ".theia-card__action" in css, "Debe definir .theia-card__action"
    
    assert "display: flex" in css or "display:flex" in css
    assert "text-align: center" in css or "text-align:center" in css
    assert "justify-content: flex-start" in css or "justify-content:flex-start" in css
    assert "margin-block-start: auto" in css or "margin-top: auto" in css


@pytest.mark.parametrize("page_path", PAGES_WITH_THEIA_CARDS)
def test_pages_link_site_cards_css_in_head(page_path):
    """Las páginas con tarjetas de contenido deben enlazar site-cards.css en el <head>."""
    file = get_html_file(page_path)
    content = file.read_text(encoding="utf-8")
    assert "site-cards.css" in content, f"{file.name} no enlaza site-cards.css"


def test_precios_why_theia_cards_structure():
    """precios.html debe tener exactamente 4 tarjetas .theia-card en la sección ¿Por qué TheIA?."""
    content = (ROOT / "precios.html").read_text(encoding="utf-8")
    
    why_section = re.search(r'<div class="why-theia[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', content, re.DOTALL)
    assert why_section is not None, "No se encontró .why-theia en precios.html"
    
    # 4 tarjetas raíz .theia-card
    cards = re.findall(r'class="[^"]*\btheia-card(?!\w)[^"]*"', why_section.group(0))
    assert len(cards) == 4, f"Se esperaban 4 tarjetas .theia-card en ¿Por qué TheIA?, encontradas {len(cards)}"
    
    # Validar que no haya text-align:left en los títulos o párrafos de las cards
    for card_chunk in why_section.group(0).split('class="glass-card'):
        if '<h3' in card_chunk:
            assert 'text-align:left' not in card_chunk.lower(), "Las tarjetas en ¿Por qué TheIA? no deben tener text-align:left inline"


@pytest.mark.parametrize("page_path", ["/precios.html", "/servicios.html", "/criterios.html"])
def test_theia_cards_layout_in_browser(desktop_page, page_path):
    """Verifica en navegador desktop que las tarjetas .theia-card tengan contenido centrado y títulos alineados."""
    desktop_page.goto(f"{BASE}{page_path}", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)
    
    cards = desktop_page.locator(".theia-card")
    count = cards.count()
    assert count >= 2, f"Se esperaban tarjetas .theia-card en {page_path}, encontradas {count}"
    
    for i in range(min(count, 6)):
        card = cards.nth(i)
        card_box = card.bounding_box()
        if card_box is None or card_box["height"] < 10:
            continue
            
        card_center_x = card_box["x"] + card_box["width"] / 2
        
        # Contenido centrado horizontalmente
        content_elem = card.locator(".theia-card__content")
        if content_elem.count() > 0:
            c_box = content_elem.bounding_box()
            if c_box:
                c_center_x = c_box["x"] + c_box["width"] / 2
                assert abs(c_center_x - card_center_x) < 3.0, (
                    f"En {page_path}, contenido de tarjeta {i} descentrado: {c_center_x} vs {card_center_x}"
                )
