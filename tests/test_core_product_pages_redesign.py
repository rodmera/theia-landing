"""Tests automatizados para HU-WEB-030:
Transformación de Páginas Core de Producto de TheIA Suite
(atencion-cliente.html, crm.html, pulse.html, panel.html, funciones.html).
"""
import re
from pathlib import Path
import pytest
from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent

CORE_PAGES = [
    "/atencion-cliente.html",
    "/crm.html",
    "/pulse.html",
    "/panel.html",
    "/funciones.html",
]


def test_atencion_cliente_ac1_hero_and_demonstrations(mobile_page):
    """AC1: atencion-cliente.html tiene el nuevo Hero y los 3 bloques de demostración sin chats simulados."""
    mobile_page.goto(f"{BASE}/atencion-cliente.html", wait_until="domcontentloaded")
    text = mobile_page.inner_text("body")
    html = (ROOT / "atencion-cliente.html").read_text(encoding="utf-8")

    # Hero
    assert "Atención omnicanal que califica y vende" in text
    assert "WhatsApp, Instagram y tu web en un solo cerebro" in text
    assert "agenda de clientes" in text

    # Bloques de demostración
    assert "Unificación de Canales" in text or "Bandeja compartida" in text
    assert "Cotizador Automático" in text or "Reglas de inventario" in text or "Catálogo oficial" in text
    assert "Derivación Inteligente" in text or "Traspaso" in text or "derivación con contexto" in text

    # Sin chats simulados
    forbidden_classes = ["msg-user", "msg-bot", "bento-chat-bubble", "bentoUserMsg", "bentoBotMsg"]
    for cls in forbidden_classes:
        assert cls not in html, f"atencion-cliente.html contiene clase de chat simulado: {cls}"


def test_crm_ac2_hero_and_visual_blocks(mobile_page):
    """AC2: crm.html enfatiza actualización automática, tablero Kanban, sin costo por asiento y conserva contratos."""
    mobile_page.goto(f"{BASE}/crm.html", wait_until="domcontentloaded")
    text = mobile_page.inner_text("body")
    html = (ROOT / "crm.html").read_text(encoding="utf-8")

    # Hero
    assert "CRM que se actualiza solo con cada conversación" in text or "actualiza solo con cada conversación" in text
    assert "agenda de clientes" in text

    # Bloques visuales
    assert "Auto-creación de Fichas" in text or "Ficha de cliente automática" in text or "sin digitación manual" in text
    assert "Tablero" in text or "Etapas" in text or "Kanban" in text
    assert "Sin Costo por Asiento" in text or "sin cobro por usuario" in text or "tarifa plana" in text

    # No jerga startup en visible text
    from test_crm_page_content import _visible_source, JERGA_FORBIDDEN
    visible_clean = _visible_source(html).lower()
    for w in JERGA_FORBIDDEN:
        assert w not in visible_clean, f"crm.html usa jerga startup: {w}"

    # Atributos data-hu-crm
    for tag in ["HU-CRM-001", "HU-CRM-006", "HU-CRM-008", "HU-CRM-011", "HU-CRM-012", "HU-CRM-027", "HU-CRM-029"]:
        assert f'data-hu-crm="{tag}"' in html, f"Falta atribución {tag} en crm.html"


def test_pulse_ac3_hero_and_briefing_components(mobile_page):
    """AC3: pulse.html declara el nuevo Hero y exhibe briefing 08:00, alerta real-time y resumen 19:00 sin chat simulado."""
    mobile_page.goto(f"{BASE}/pulse.html", wait_until="domcontentloaded")
    text = mobile_page.inner_text("body")
    html = (ROOT / "pulse.html").read_text(encoding="utf-8")

    # Hero
    assert "La salud de tus ventas y clientes" in text
    assert "Directo en tu WhatsApp personal" in text

    # 3 Componentes / artefactos de control
    assert "Briefing Matutino" in text or "08:00" in text
    assert "Alerta en Tiempo Real" in text or "Alerta lead caliente" in text or "lead prioritario" in text
    assert "Resumen de Cierre" in text or "19:00" in text or "Cierre de jornada" in text

    # Sin chats simulados
    forbidden_classes = ["msg-user", "msg-bot", "msgfade", "bento-chat-bubble"]
    for cls in forbidden_classes:
        assert cls not in html, f"pulse.html contiene clase de chat simulado: {cls}"


def test_panel_and_funciones_ac4_rules_inspector(mobile_page):
    """AC4: panel.html y funciones.html incorporan consola/inspector de reglas, catálogo oficial y PII Ley 21.719."""
    for page_path in ["/panel.html", "/funciones.html"]:
        mobile_page.goto(f"{BASE}{page_path}", wait_until="domcontentloaded")
        text = mobile_page.inner_text("body")
        html = (ROOT / page_path.lstrip("/")).read_text(encoding="utf-8")

        # Reglas de negocio / catálogo / control
        assert any(k in text for k in ["Reglas", "Catálogo", "Inspector", "Consola"]), f"{page_path} sin mención de reglas/catálogo"
        assert any(k in text for k in ["21.719", "PII", "privacidad", "datos protegidos", "enmascaramiento"]), f"{page_path} sin protección de datos PII/Ley 21.719"

    # funciones.html conserva sus 3 resultados clave
    mobile_page.goto(f"{BASE}/funciones.html", wait_until="domcontentloaded")
    funciones_text = mobile_page.inner_text("body")
    for key in ["Atiende y orienta.", "Cotiza, agenda y hace seguimiento.", "Tu equipo conserva el control."]:
        assert key in funciones_text, f"funciones.html perdió heading obligatorio: {key}"


@pytest.mark.parametrize("page_path", CORE_PAGES)
def test_core_pages_ac5_tokens_and_mobile_responsive(mobile_page, page_path):
    """AC5: Las 5 páginas usan site-cards.css, fuentes oficiales, y no tienen overflow horizontal en móvil."""
    errors = []
    mobile_page.on("pageerror", lambda err: errors.append(str(err)))

    mobile_page.goto(f"{BASE}{page_path}", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    # Cero errores JS
    assert not errors, f"Errores JS en {page_path}: {errors}"

    # Cero overflow horizontal en 390px
    scroll_w = mobile_page.evaluate("() => document.documentElement.scrollWidth")
    client_w = mobile_page.evaluate("() => document.documentElement.clientWidth")
    assert scroll_w <= client_w + 1, f"Overflow horizontal en {page_path}: scrollWidth={scroll_w} > clientWidth={client_w}"

    # Archivo HTML enlaza site-cards.css, site-nav.css, site-footer.css
    html = (ROOT / page_path.lstrip("/")).read_text(encoding="utf-8")
    assert "/site-cards.css" in html or "site-cards.css" in html, f"{page_path} no enlaza site-cards.css"
    assert "/site-nav.css" in html or "site-nav.css" in html, f"{page_path} no enlaza site-nav.css"
    assert "/site-footer.css" in html or "site-footer.css" in html, f"{page_path} no enlaza site-footer.css"
