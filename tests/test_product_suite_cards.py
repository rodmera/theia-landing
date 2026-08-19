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
    """product-suite.css debe definir el contrato completo de clases y layout."""
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
    
    # Contrato de layout
    assert "display: grid" in css or "display:grid" in css, "grid layout en .product-suite-grid"
    assert "display: flex" in css or "display:flex" in css, "flex layout en .product-suite-card"
    assert "text-align: center" in css or "text-align:center" in css, "centrado de texto en tarjeta"
    assert "margin-block-start: auto" in css or "margin-top: auto" in css, "CTA anclado a la base"


@pytest.mark.parametrize("html_file,expected_ctas", [
    (INDEX_HTML, [
        ("/atencion-cliente", "Conocer Atención"),
        ("/pulse", "Conocer Pulse"),
        ("openTheiaChat('crm')", "Conocer CRM"),
        ("/panel", "Ver Panel de Control"),
    ]),
    (ATENCION_HTML, [
        ("/funciones", "Ver cómo ayuda"),
        ("/pulse", "Conocer Pulse"),
        ("openTheiaChat('crm')", "Conocer CRM"),
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
        assert dist_to_bottom < 45.0, f"En {path}, acción {i} no está anclada al fondo (dist={dist_to_bottom}px)"

    # 2. Las acciones en tarjetas de la misma fila deben tener la misma posición vertical inferior (alineadas a la misma base)
    action_bottoms_by_row = {}
    for i in range(count):
        card = cards.nth(i)
        card_box = card.bounding_box()
        action = card.locator(".product-suite-card__action")
        action_box = action.bounding_box()
        
        # Agrupar por fila (aproximación por card_box['y'])
        row_key = round(card_box["y"] / 10) * 10
        action_bottom = action_box["y"] + action_box["height"]
        action_bottoms_by_row.setdefault(row_key, []).append(action_bottom)
        
    for row_key, bottoms in action_bottoms_by_row.items():
        if len(bottoms) > 1:
            max_diff = max(bottoms) - min(bottoms)
            assert max_diff < 3.0, f"En {path}, las acciones en la fila {row_key} no tienen la misma base (diff={max_diff}px)"


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

