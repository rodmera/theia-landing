import pytest
from playwright.sync_api import Page
from conftest import BASE

PAGES_TO_AUDIT = [
    ("index.html", [".specialist-card__icon", ".setup-case-icon", ".conecta-card-icon", ".triada-card__icon", ".piece-icon-wrap"]),
    ("cerebro.html", [".lean-icon"]),
    ("pulse.html", [".pulse-feat-icon"]),
    ("crm.html", [".feature-icon", ".complemento-icon"]),
    ("nosotros.html", [".piece-icon-wrap"]),
    ("atencion-cliente.html", [".piece-icon", ".piece-icon-wrap"]),
    ("precios.html", [".piece-icon-wrap"]),
    ("servicios.html", [".extra-icon", ".piece-icon-wrap"]),
]

@pytest.mark.parametrize("page_name,selectors", PAGES_TO_AUDIT)
def test_card_visual_icons_strictly_homologated_52px(desktop_page: Page, page_name: str, selectors: list):
    """Garantiza que todos los apoyos visuales de tarjetas midan estrictamente 52x52px en el DOM renderizado."""
    desktop_page.goto(f"{BASE}/{page_name}", wait_until="domcontentloaded")
    
    for sel in selectors:
        loc = desktop_page.locator(sel)
        count = loc.count()
        if count > 0:
            for i in range(count):
                el = loc.nth(i)
                box = el.bounding_box()
                assert box is not None, f"En {page_name}, elemento {sel}[{i}] no tiene bounding box visible"
                assert abs(box["width"] - 52.0) <= 2.0, (
                    f"VIOLACIÓN DE HOMOLOGACIÓN en {page_name} ({sel}[{i}]): "
                    f"ancho={box['width']:.1f}px (debe ser 52px)"
                )
                assert abs(box["height"] - 52.0) <= 2.0, (
                    f"VIOLACIÓN DE HOMOLOGACIÓN en {page_name} ({sel}[{i}]): "
                    f"alto={box['height']:.1f}px (debe ser 52px)"
                )

def test_no_overloaded_pills_or_secondary_badges_in_cards(desktop_page: Page):
    """Garantiza que ninguna tarjeta contenga pastillas amontonadas o badges secundarios compitiendo."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    
    # Prohibición de pastillas secundarias en tarjetas
    forbidden_pills = desktop_page.locator(".specialist-tool-pill, .card-pill, .triada-card__pills").count()
    assert forbidden_pills == 0, f"Se detectaron {forbidden_pills} pastillas sobrecargadas en tarjetas de index.html"
    
    # Prohibición de badges secundarios en cabecera de tarjetas
    forbidden_badges = desktop_page.locator(".specialist-card__badge, .conecta-card-badge, .triada-card__badge").count()
    assert forbidden_badges == 0, f"Se detectaron {forbidden_badges} badges secundarios compitiendo en tarjetas de index.html"
