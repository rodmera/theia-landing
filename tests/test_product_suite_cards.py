"""Pruebas del módulo CSS product-suite y de la alineación de las tarjetas de productos.

Verifica el contrato de arquitectura y layout para las 4 tarjetas principales
(Atención, Pulse, CRM, Plataforma) en index.html y atencion-cliente.html:
- Contrato CSS (product-suite.css): clases semánticas, flexbox, centrado y auto-margin.
- Estructura HTML: presencia de clases y jerarquía semántica sin regresiones de copy o CTAs.
- Verificación en navegador (Playwright): centrado horizontal y alineación vertical de CTAs en la base.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"
ATENCION_HTML = ROOT / "atencion-cliente.html"
CSS_FILE = ROOT / "product-suite.css"


def test_product_suite_css_file_exists():
    """product-suite.css debe existir en la raíz del repositorio."""
    assert CSS_FILE.is_file(), "product-suite.css no existe en la raíz"


def test_pages_link_product_suite_css():
    """index.html y atencion-cliente.html deben enlazar product-suite.css."""
    for html_file in [INDEX_HTML, ATENCION_HTML]:
        content = html_file.read_text(encoding="utf-8")
        assert "product-suite.css" in content, f"{html_file.name} no enlaza product-suite.css"


def test_product_suite_css_contains_semantic_contract():
    """product-suite.css debe definir el contrato completo de clases y layout simétrico."""
    css = CSS_FILE.read_text(encoding="utf-8")
    
    # Clases requeridas por el contrato de arquitectura
    required_classes = [
        ".product-suite-grid",
        ".product-suite-card",
        ".product-suite-card__header",
        ".product-suite-card__icon",
        ".product-suite-card__content",
        ".product-suite-card__action",
    ]
    for cls in required_classes:
        assert cls in css, f"product-suite.css debe definir {cls}"
    
    # Contrato de layout simétrico
    assert "display: grid" in css or "display:grid" in css, "grid layout en .product-suite-grid"
    assert "display: flex" in css or "display:flex" in css, "flex layout en .product-suite-card"
    assert "text-align: center" in css or "text-align:center" in css, "centrado de texto en tarjeta"
    assert "justify-content: flex-start" in css or "justify-content:flex-start" in css, "alineación superior del contenido"
    assert "margin-block-start: auto" in css or "margin-top: auto" in css, "CTA anclado a la base"


@pytest.mark.parametrize("html_file,expected_ctas", [
    (INDEX_HTML, [
        ("/atencion-cliente", "Conocer Atención"),
        ("/pulse", "Conocer Pulse"),
        ("/crm", "Conocer CRM"),
        ("/panel", "Ver Panel de Control"),
    ]),
    (ATENCION_HTML, [
        ("/funciones", "Ver cómo ayuda"),
        ("/pulse", "Conocer Pulse"),
        ("/crm", "Conocer CRM"),
        ("/panel", "Ver Panel de Control"),
    ]),
])
def test_html_structure_has_4_cards_with_correct_semantics_and_ctas(html_file, expected_ctas):
    """Verifica que el HTML contiene exactamente 4 tarjetas con la jerarquía semántica y CTAs intactos."""
    content = html_file.read_text(encoding="utf-8")
    
    assert "product-suite-grid" in content, f"{html_file.name} debe contener .product-suite-grid"
    
    cards_count = content.count("product-suite-card__header")
    assert cards_count == 4, f"{html_file.name} debe contener 4 tarjetas con .product-suite-card__header (encontradas {cards_count})"
    
    content_count = content.count("product-suite-card__content")
    assert content_count == 4, f"{html_file.name} debe contener 4 bloques .product-suite-card__content"
    
    action_count = content.count("product-suite-card__action")
    assert action_count == 4, f"{html_file.name} debe contener 4 acciones .product-suite-card__action"
    
    # Títulos esperados
    for title in ["Atención", "TheIA Pulse", "CRM", "Panel de Control"]:
        assert title in content, f"{html_file.name} debe contener el producto '{title}'"
        
    # CTAs esperados
    for href_or_onclick, label in expected_ctas:
        assert href_or_onclick in content, f"{html_file.name} debe preservar el enlace/handler '{href_or_onclick}'"
        assert label in content, f"{html_file.name} debe preservar el texto del botón '{label}'"


@pytest.mark.parametrize("path", ["/", "/atencion-cliente.html"])
def test_product_suite_card_layout_in_browser(desktop_page, path):
    """Verifica en navegador real que las tarjetas estén centradas horizontalmente y los CTAs alineados al fondo."""
    desktop_page.goto(f"{BASE}{path}", wait_until="domcontentloaded")
    cards = desktop_page.locator(".product-suite-grid .product-suite-card")
    cards.first.scroll_into_view_if_needed()
    desktop_page.wait_for_timeout(350)
    
    cards = desktop_page.locator(".product-suite-grid .product-suite-card")
    count = cards.count()
    assert count == 4, f"Se esperaban 4 tarjetas .product-suite-card en {path}, se encontraron {count}"
    
    # 1. Centrado horizontal de contenido y botón respecto a la tarjeta
    for i in range(count):
        card = cards.nth(i)
        card_box = card.bounding_box()
        assert card_box is not None, f"Tarjeta {i} sin bounding box"
        card_center_x = card_box["x"] + card_box["width"] / 2
        
        # Header / Icono centrado
        header = card.locator(".product-suite-card__header")
        header_box = header.bounding_box()
        assert header_box is not None, f"Header {i} sin bounding box"
        header_center_x = header_box["x"] + header_box["width"] / 2
        assert abs(header_center_x - card_center_x) < 3.0, (
            f"En {path}, header {i} descentrado: card_center={card_center_x}, header_center={header_center_x}"
        )
        
        # Botón / Acción centrado
        action = card.locator(".product-suite-card__action")
        action_box = action.bounding_box()
        assert action_box is not None, f"Action {i} sin bounding box"
        action_center_x = action_box["x"] + action_box["width"] / 2
        assert abs(action_center_x - card_center_x) < 3.0, (
            f"En {path}, action {i} descentrado: card_center={card_center_x}, action_center={action_center_x}"
        )
        
        # El CTA debe estar cerca de la base de la tarjeta (espacio inferior uniforme)
        dist_to_bottom = (card_box["y"] + card_box["height"]) - (action_box["y"] + action_box["height"])
        assert dist_to_bottom >= 0, f"En {path}, acción {i} excede la tarjeta"
        assert dist_to_bottom < 55.0, f"En {path}, acción {i} no está anclada al fondo (dist={dist_to_bottom}px)"

    # 2. Las acciones, títulos y párrafos en tarjetas de la misma fila deben compartir la misma alineación vertical
    h3_tops_by_row = {}
    p_tops_by_row = {}
    action_bottoms_by_row = {}
    
    for i in range(count):
        card = cards.nth(i)
        card_box = card.bounding_box()
        
        h3 = card.locator(".product-suite-card__content h3")
        h3_box = h3.bounding_box()
        assert h3_box is not None, f"H3 {i} sin bounding box"
        
        p_elem = card.locator(".product-suite-card__content p")
        p_box = p_elem.bounding_box()
        assert p_box is not None, f"P {i} sin bounding box"
        
        action = card.locator(".product-suite-card__action")
        action_box = action.bounding_box()
        assert action_box is not None, f"Action {i} sin bounding box"
        
        # Agrupar por fila (aproximación por card_box['y'])
        row_key = round(card_box["y"] / 10) * 10
        h3_tops_by_row.setdefault(row_key, []).append(h3_box["y"])
        p_tops_by_row.setdefault(row_key, []).append(p_box["y"])
        action_bottoms_by_row.setdefault(row_key, []).append(action_box["y"] + action_box["height"])
        
    for row_key in h3_tops_by_row:
        h3_tops = h3_tops_by_row[row_key]
        p_tops = p_tops_by_row[row_key]
        bottoms = action_bottoms_by_row[row_key]
        
        if len(h3_tops) > 1:
            diff_h3 = max(h3_tops) - min(h3_tops)
            assert diff_h3 < 5.0, f"En {path}, los títulos h3 en fila {row_key} no inician a la misma altura (diff={diff_h3}px)"
            
            diff_p = max(p_tops) - min(p_tops)
            assert diff_p < 5.0, f"En {path}, los párrafos p en fila {row_key} no inician a la misma altura (diff={diff_p}px)"
            
            max_diff = max(bottoms) - min(bottoms)
            assert max_diff < 5.0, f"En {path}, las acciones en la fila {row_key} no tienen la misma base (diff={max_diff}px)"


def test_product_suite_card_copy_balance_and_homogeneity():
    """Verifica que los 4 párrafos tengan longitud equilibrada (18-26 palabras) e idéntica entre index y atencion-cliente."""
    index_content = INDEX_HTML.read_text(encoding="utf-8")
    atencion_content = ATENCION_HTML.read_text(encoding="utf-8")
    
    # Extraer los 4 párrafos de product-suite-card__content
    pattern = re.compile(r'<div class="product-suite-card__content">\s*<h3[^>]*>([^<]+)</h3>\s*<p[^>]*>([^<]+)</p>', re.DOTALL)
    
    index_matches = pattern.findall(index_content)
    atencion_matches = pattern.findall(atencion_content)
    
    assert len(index_matches) == 4, f"Se esperaban 4 tarjetas en index.html, encontradas {len(index_matches)}"
    assert len(atencion_matches) == 4, f"Se esperaban 4 tarjetas en atencion-cliente.html, encontradas {len(atencion_matches)}"
    
    for i in range(4):
        title_idx, p_idx = index_matches[i]
        title_atn, p_atn = atencion_matches[i]
        
        # Mismo título y copy entre páginas
        assert title_idx.strip() == title_atn.strip(), f"Título mismatch en tarjeta {i}: '{title_idx}' vs '{title_atn}'"
        assert p_idx.strip() == p_atn.strip(), f"Copy mismatch en tarjeta {i}: '{p_idx.strip()}' vs '{p_atn.strip()}'"
        
        words = len(p_idx.strip().split())
        assert 18 <= words <= 26, f"Tarjeta {title_idx} tiene longitud no balanceada: {words} palabras ({p_idx.strip()})"


@pytest.mark.parametrize("path", ["/", "/atencion-cliente.html"])
def test_product_suite_card_mobile_layout(mobile_page, path):
    """Verifica en viewport móvil que las tarjetas se adapten sin overflow horizontal y centradas."""
    mobile_page.goto(f"{BASE}{path}", wait_until="domcontentloaded")
    
    cards = mobile_page.locator(".product-suite-grid .product-suite-card")
    count = cards.count()
    assert count == 4, f"Se esperaban 4 tarjetas .product-suite-card en {path} móvil, se encontraron {count}"
    
    for i in range(count):
        card = cards.nth(i)
        card_box = card.bounding_box()
        assert card_box is not None
        assert card_box["width"] > 200
        card_center_x = card_box["x"] + card_box["width"] / 2
        
        # Acción centrada en móvil
        action = card.locator(".product-suite-card__action")
        action_box = action.bounding_box()
        assert action_box is not None
        action_center_x = action_box["x"] + action_box["width"] / 2
        assert abs(action_center_x - card_center_x) < 3.0, (
            f"En {path} móvil, action {i} descentrado: card_center={card_center_x}, action_center={action_center_x}"
        )

