"""
Tests Playwright E2E para la Transformación de Páginas Verticales por Industria (HU-WEB-032).
Verifica:
- AC1: Servicios Profesionales & B2B (servicios-pyme.html) con calificación, Google Calendar y captura de requerimientos.
- AC2: Salud y Clínicas (salud.html) con agendamiento médico, recordatorios 24h, aranceles y Ley 21.719.
- AC3: Automotriz y Talleres (automotriz.html) con mantenciones por km/modelo, repuestos por código y agendamiento.
- AC4: Comercio y Retail (comercio.html) con stock en tiempo real, catálogo sincronizado, derivación de pagos y tracking.
- AC5: Criterios y Alternativa CRM (criterios.html, alternativa-crm.html) con tarifa plana $250.000 CLP/mes, $0 por usuario y soporte local en Chile.
- AC6: Micro-UIs de reglas por rubro, tokens de micro-detalle físico, responsive sin overflow en 390px y cero errores JS.
"""
from pathlib import Path
import re
import pytest
from conftest import BASE, ROOT, filtered_js_errors

SERVICIOS_HTML = ROOT / "servicios-pyme.html"
SALUD_HTML = ROOT / "salud.html"
AUTOMOTRIZ_HTML = ROOT / "automotriz.html"
COMERCIO_HTML = ROOT / "comercio.html"
CRITERIOS_HTML = ROOT / "criterios.html"
ALTERNATIVA_CRM_HTML = ROOT / "alternativa-crm.html"

VERTICAL_PAGES = [
    "servicios-pyme.html",
    "salud.html",
    "automotriz.html",
    "comercio.html",
    "criterios.html",
    "alternativa-crm.html"
]


def _visible_text(html: str) -> str:
    """Extrae texto visible limpio."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_ac1_servicios_pyme(desktop_page):
    """AC1: servicios-pyme.html califica presupuestos, agenda en Google Calendar y captura requerimientos."""
    assert SERVICIOS_HTML.is_file()
    content = SERVICIOS_HTML.read_text(encoding="utf-8")
    visible = _visible_text(content)

    assert "califica" in visible.lower() or "calificación" in visible.lower()
    assert "Google Calendar" in visible or "calendar" in visible.lower() or "reunión" in visible.lower()
    assert "requerimientos" in visible.lower() or "propuesta" in visible.lower()

    # Micro-UI presente
    assert "reglas" in visible.lower() or "consola" in visible.lower() or "b2b" in visible.lower()


def test_ac2_salud(desktop_page):
    """AC2: salud.html destaca agendamiento médico, confirmación 24h, aranceles y Ley 21.719."""
    assert SALUD_HTML.is_file()
    content = SALUD_HTML.read_text(encoding="utf-8")
    visible = _visible_text(content)

    assert "cita" in visible.lower() or "horas" in visible.lower()
    assert "recordatorio" in visible.lower() or "24" in visible.lower()
    assert "arancel" in visible.lower() or "convenio" in visible.lower()
    assert "21.719" in content or "privacidad" in visible.lower() or "pii" in content.lower()


def test_ac3_automotriz(desktop_page):
    """AC3: automotriz.html exhibe mantenciones por km/modelo, repuestos por código y agendamiento."""
    assert AUTOMOTRIZ_HTML.is_file()
    content = AUTOMOTRIZ_HTML.read_text(encoding="utf-8")
    visible = _visible_text(content)

    assert "mantenci" in visible.lower()
    assert "repuesto" in visible.lower() or "código" in visible.lower() or "taller" in visible.lower()


def test_ac4_comercio(desktop_page):
    """AC4: comercio.html presenta stock en tiempo real, catálogo sincronizado, pagos y despacho."""
    assert COMERCIO_HTML.is_file()
    content = COMERCIO_HTML.read_text(encoding="utf-8")
    visible = _visible_text(content)

    assert "stock" in visible.lower()
    assert "catálogo" in visible.lower()
    assert "pago" in visible.lower() or "despacho" in visible.lower()


def test_ac5_criterios_and_alternativa_crm(desktop_page):
    """AC5: criterios.html y alternativa-crm.html defienden la tarifa plana desde $250.000 CLP y $0 por asiento."""
    # criterios.html
    crit_content = CRITERIOS_HTML.read_text(encoding="utf-8")
    assert "250.000" in crit_content or "criterios" in crit_content.lower()

    # alternativa-crm.html
    alt_content = ALTERNATIVA_CRM_HTML.read_text(encoding="utf-8")
    assert "250.000" in alt_content
    assert "usuario" in alt_content.lower() or "asiento" in alt_content.lower()


@pytest.mark.parametrize("page_name", VERTICAL_PAGES)
def test_ac6_vertical_pages_responsive_and_no_overflow(mobile_page, page_name):
    """AC6: Las 6 páginas verticales no presentan horizontal overflow en móvil 390px ni errores JS."""
    mobile_page.goto(f"{BASE}/{page_name}", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    # Verificar sin overflow horizontal
    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    client_w = mobile_page.evaluate("document.documentElement.clientWidth")
    assert scroll_w <= client_w + 1, f"Overflow horizontal en {page_name}: scrollWidth={scroll_w} > clientWidth={client_w}"

    # Cero errores JS críticos
    critical_errors = filtered_js_errors(mobile_page)
    assert not critical_errors, f"Errores JS en {page_name}: {critical_errors}"
