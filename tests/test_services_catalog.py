"""Pruebas del catálogo de 9 servicios especializados en 3 ejes estratégicos (TASK-202608192340).

Verifica:
1. Estructura de 3 ejes estratégicos en servicios.html:
   - Eje 1: Arquitectura de Agentes & Orquestación (3 servicios)
   - Eje 2: Integración, Contexto & Datos Empresariales (3 servicios)
   - Eje 3: Voz, Copilotos & Operación Continua (3 servicios)
2. Total de 9 servicios con semántica .theia-card (.theia-card__visual, .theia-card__content).
3. Eliminación de cards legacy no pertenecientes al catálogo (Marketing Digital plano / Presencia Digital genérica).
4. Verificación en navegador Playwright en desktop y mobile sin desbordes horizontales.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
SERVICIOS_HTML = ROOT / "servicios.html"


def test_servicios_has_three_axes_and_nine_services():
    """servicios.html debe organizar 9 servicios especializados en 3 ejes estratégicos de alto valor."""
    content = SERVICIOS_HTML.read_text(encoding="utf-8")
    
    # 1. Tres ejes estratégicos
    assert "Arquitectura de Agentes" in content or "Orquestación" in content, "Falta Eje 1: Arquitectura de Agentes"
    assert "Integración" in content and ("Datos" in content or "Contexto" in content), "Falta Eje 2: Integración, Contexto & Datos"
    assert "Voz" in content or "Copilotos" in content or "Operación Continua" in content, "Falta Eje 3: Voz, Copilotos & Operación Continua"
    
    # 2. Nueve servicios especializados
    nine_services = [
        "Orquestación Multi-Agente",
        "Agent Harness",
        "Vigilancia Efímera",
        "Conectores Zero-Prompt",
        "Document AI",
        "Integraciones y APIs",
        "Copilotos Ejecutivos",
        "Atención por Voz",
        "Auditoría de Conversaciones",
    ]
    for s in nine_services:
        assert s in content, f"servicios.html debe contener el servicio especializado '{s}'"
        
    # 3. Exactamente 9 tarjetas .theia-card en servicios.html
    theia_cards = re.findall(r'class="[^"]*\btheia-card\b[^"]*"', content)
    assert len(theia_cards) == 9, f"Se esperaban 9 tarjetas .theia-card en servicios.html, encontradas {len(theia_cards)}"
    
    # 4. No debe incluir las cards genéricas descartadas del catálogo
    assert "Análisis de Presencia Digital 360°" not in content, "Debe retirar la card legacy de Presencia Digital"
    assert "TheIA Growth" not in content, "Debe retirar la card legacy TheIA Growth"


def test_servicios_layout_in_browser_desktop(desktop_page):
    """Verifica en desktop que los 3 ejes y las 9 tarjetas rendericen de forma simétrica."""
    desktop_page.goto(f"{BASE}/servicios.html", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)
    
    cards = desktop_page.locator(".theia-card")
    assert cards.count() == 9, f"Se esperaban 9 tarjetas .theia-card en desktop, encontradas {cards.count()}"
    
    # Centrado de contenido en cada una de las 9 tarjetas
    for i in range(9):
        card = cards.nth(i)
        card_box = card.bounding_box()
        assert card_box is not None
        card_center_x = card_box["x"] + card_box["width"] / 2
        
        content = card.locator(".theia-card__content")
        c_box = content.bounding_box()
        assert c_box is not None
        c_center_x = c_box["x"] + c_box["width"] / 2
        assert abs(c_center_x - card_center_x) < 3.0, f"Tarjeta {i} descentrada en servicios.html"


def test_servicios_layout_in_browser_mobile(mobile_page):
    """Verifica en mobile que las 9 tarjetas se adapten limpiamente sin desbordes horizontales."""
    mobile_page.goto(f"{BASE}/servicios.html", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)
    
    cards = mobile_page.locator(".theia-card")
    assert cards.count() == 9
    
    has_overflow = mobile_page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
    assert not has_overflow, "servicios.html tiene overflow horizontal en mobile"
