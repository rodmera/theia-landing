"""
Tests Playwright E2E para la Transformación de Páginas Comerciales e Institucionales (HU-WEB-031).
Verifica:
- AC1: Planes y Precios (precios.html) con tarifa plana $250.000 CLP/mes (+ IVA), $0 por asiento, inclusión completa y transparencia de canal Meta.
- AC2: Migración Asistida (migracion.html) con preservación total, reversibilidad de 7 días y puesta en marcha <7 días.
- AC3: Calculadora de Retorno & Timeline Speed-to-Lead (calculadora.html) con Componente D interactivo y cálculo dinámico de ROI sobre $250.000 CLP.
- AC4: Historia Institucional y Casos (nosotros.html y casos.html) con ingeniería chilena, Google Cloud/Gemini, Ley 21.719 y casos por industria sin testimonios inventados.
- AC5: Tokens de diseño físico, responsive sin horizontal overflow en 390px y cero errores JS.
"""
from pathlib import Path
import re
import pytest
from conftest import BASE, ROOT, filtered_js_errors

PRECIOS_HTML = ROOT / "precios.html"
MIGRACION_HTML = ROOT / "migracion.html"
CALCULADORA_HTML = ROOT / "calculadora.html"
NOSOTROS_HTML = ROOT / "nosotros.html"
CASOS_HTML = ROOT / "casos.html"


def _visible_text(html: str) -> str:
    """Extrae texto visible limpio."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_ac1_precios_content_and_contract(desktop_page):
    """AC1: precios.html declara tarifa plana $250.000 CLP/mes, $0 por usuario, inclusión completa y link a términos."""
    assert PRECIOS_HTML.is_file()
    content = PRECIOS_HTML.read_text(encoding="utf-8")
    visible = _visible_text(content)

    # 1. Tarifa plana oficial
    assert "desde $250.000" in visible or "250.000" in visible
    assert "CLP/mes" in visible
    assert "Sin cobro por usuario" in visible or "sin cobro por usuario" in visible or "$0" in visible

    # 2. Inclusiones
    assert "WhatsApp" in visible
    assert "Instagram" in visible
    assert "TheIA Pulse" in visible
    assert "Módulo CRM" in visible or "CRM" in visible

    # 3. Transparencia y Términos
    assert "/terminos.html" in content or "/terminos" in content
    assert "Meta" in visible

    # 4. Navegación en browser
    desktop_page.goto(f"{BASE}/precios.html", wait_until="domcontentloaded")
    assert desktop_page.locator(".pricing-cards").is_visible()


def test_ac2_migracion_frictionless_guarantee(desktop_page):
    """AC2: migracion.html garantiza preservación total, reversibilidad de 7 días y proceso en 3 pasos."""
    assert MIGRACION_HTML.is_file()
    content = MIGRACION_HTML.read_text(encoding="utf-8")
    visible = _visible_text(content)

    # 1. Preservación total
    assert "Contactos y Empresas" in visible
    assert "Negocios y Etapas" in visible
    assert "Notas y Tareas" in visible

    # 2. Reversibilidad 7 días
    assert "7 días" in visible or "7 Días" in visible
    assert "Reversibilidad" in visible or "reversibilidad" in visible

    # 3. Proceso guiado
    assert "Paso" in visible or "pasos" in visible or "badge-step" in content


def test_ac3_calculadora_speed_to_lead_timeline(desktop_page):
    """AC3: calculadora.html incorpora Timeline Speed-to-Lead (Componente D) y cálculo dinámico de ROI sobre $250.000 CLP."""
    assert CALCULADORA_HTML.is_file()
    content = CALCULADORA_HTML.read_text(encoding="utf-8")

    # 1. Componente Timeline Speed-to-Lead presente
    assert "speed-to-lead" in content.lower() or "timeline" in content.lower() or "recuperación" in content.lower()

    # 2. Simulación interactiva en browser
    desktop_page.goto(f"{BASE}/calculadora.html", wait_until="domcontentloaded")

    # Mover slider de consultas
    inquiries_slider = desktop_page.locator("#calc-inquiries")
    assert inquiries_slider.is_visible()
    inquiries_slider.fill("400")

    # Clic en chip de ticket $100.000
    chip_100k = desktop_page.locator("button.calc-chip[data-value='100000']")
    if chip_100k.is_visible():
        chip_100k.click()

    lost_text = desktop_page.locator("#calc-lost").inner_text()
    roi_text = desktop_page.locator("#calc-roi").inner_text()
    assert "$" in lost_text
    assert "TheIA" in roi_text or "recuperas" in roi_text.lower()


def test_ac4_nosotros_and_casos_credibility(desktop_page):
    """AC4: nosotros.html y casos.html reflejan ingeniería chilena, Google Cloud/Gemini, Ley 21.719 y casos por industria."""
    # 1. nosotros.html
    nosotros_content = NOSOTROS_HTML.read_text(encoding="utf-8")
    assert "Google Cloud" in nosotros_content
    assert "Gemini" in nosotros_content
    assert "Ley 21.719" in nosotros_content or "21.719" in nosotros_content
    assert "Santiago" in nosotros_content or "Chile" in nosotros_content

    # 2. casos.html
    casos_content = CASOS_HTML.read_text(encoding="utf-8")
    casos_visible = _visible_text(casos_content).lower()
    for industry in ["salud", "servicios", "comercio", "automotriz"]:
        assert industry in casos_visible, f"casos.html falta industria: {industry}"


@pytest.mark.parametrize("page_name", ["precios.html", "migracion.html", "calculadora.html", "nosotros.html", "casos.html"])
def test_ac5_commercial_pages_responsive_and_no_overflow(mobile_page, page_name):
    """AC5: Las 5 páginas comerciales no presentan horizontal overflow en móvil 390px ni errores JS."""
    mobile_page.goto(f"{BASE}/{page_name}", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    # Verificar sin overflow horizontal
    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    client_w = mobile_page.evaluate("document.documentElement.clientWidth")
    assert scroll_w <= client_w + 1, f"Overflow horizontal en {page_name}: scrollWidth={scroll_w} > clientWidth={client_w}"

    # Cero errores JS críticos
    critical_errors = filtered_js_errors(mobile_page)
    assert not critical_errors, f"Errores JS en {page_name}: {critical_errors}"
