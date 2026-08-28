"""Tests E2E Playwright para HU-WEB-029: Transformación de Home a Partner de IA y Consola de Reglas.

Verifica:
- AC1: Erradicación de chats simulados y sustitución por micro-UIs de reglas (catálogo $185.000 CLP, freno de descuentos y CRM).
- AC2: Alineación de sección problema con realidad chilena (ventas nocturnas/terreno, speed-to-lead 78%, oportunidad lista para vendedor).
- AC3: Diagrama de orquestación omnicanal SVG (WhatsApp, Instagram, Web -> TheIA Engine -> Reglas -> CRM/Pulse) y Bento Grid 2.0 asimétrico.
- AC4: Cumplimiento de los 5 tokens de micro-detalle físico en site-cards.css y tokens canónicos de diseño.
- AC5: Renderizado responsivo, sin overflow horizontal en mobile y cero errores JS.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE, ROOT, filtered_js_errors

INDEX_HTML = ROOT / "index.html"
SITE_CARDS_CSS = ROOT / "site-cards.css"
HOME_UI_CSS = ROOT / "home-product-ui.css"
HOME_UI_JS = ROOT / "home-product-ui.js"


def test_ac1_no_simulated_dialogues_and_rules_micro_uis_present():
    """HU-WEB-029 AC1: Erradicación de diálogos simulados y sustitución por micro-UIs de reglas."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    # 1. No diálogos simulados artificiales ni burbujas ficticias
    assert "Hola, soy una clínica dental con 8 sillones" not in content, "No debe haber diálogos simulados artificiales"
    assert "bento-chat-bubble" not in content, "No deben existir estilos o clases de burbujas de chat ficticias"
    assert "bentoUserMsg" not in content, "No deben existir animaciones de mensajes de chat ficticios"

    # 2. Micro-UIs de control y reglas reales
    # Catálogo y precio oficial ($185.000 CLP)
    assert "$185.000" in content, "Debe mostrar validación de precio oficial $185.000 CLP"
    assert "Catálogo Oficial" in content or "catálogo oficial" in content.lower(), "Debe validar aplicación de catálogo oficial"

    # Freno de descuentos y políticas
    assert "Descuento" in content or "descuento" in content, "Debe ilustrar política de descuentos"
    assert "Bloqueado" in content or "Protegido" in content, "Debe ilustrar estado de protección/freno de seguridad"

    # Trazabilidad CRM
    assert "CRM" in content, "Debe incluir trazabilidad en CRM"
    assert "Ficha" in content or "ficha" in content, "Debe ilustrar creación de ficha o registro de cliente"


def test_ac2_problem_section_aligned_to_speed_to_lead_and_chilean_business():
    """HU-WEB-029 AC2: Sección problema enfocada en ventas nocturnas, terreno, speed-to-lead 78% y cierre."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    problema_match = re.search(r'<section class="problema".*?</section>', content, re.DOTALL)
    assert problema_match is not None, "Debe existir la sección .problema en index.html"
    problema_text = problema_match.group(0)

    # Pérdida de ventas nocturnas / fines de semana / terreno
    assert ("nocturn" in problema_text.lower() or "fines de semana" in problema_text.lower() or "fuera de horario" in problema_text.lower()), (
        "Sección problema debe mencionar pérdida de ventas nocturnas o fuera de horario"
    )
    assert ("terreno" in problema_text.lower() or "ocupado" in problema_text.lower() or "operando" in problema_text.lower()), (
        "Sección problema debe mencionar atención en terreno u ocupación operativa"
    )

    # Métrica Speed-to-lead 78%
    assert "78%" in problema_text, "Sección problema debe citar la métrica del 78% de speed-to-lead"

    # TheIA como motor que deja la oportunidad lista para el vendedor
    assert ("vendedor" in problema_text.lower() or "equipo" in problema_text.lower()), (
        "Sección problema debe posicionar a TheIA preparando la oportunidad para el vendedor/equipo"
    )


def test_ac3_omnichannel_orchestration_svg_diagram_and_bento_grid():
    """HU-WEB-029 AC3: Diagrama de orquestación omnicanal SVG y Bento Grid 2.0."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    # Componente B: Diagrama de Orquestación Omnicanal SVG
    assert "home-ui__orchestration" in content or "orchestration-diagram" in content or "home-orchestration" in content, (
        "index.html debe contener el contenedor del Diagrama de Orquestación Omnicanal"
    )
    # Canales oficiales presentes con sus colores de marca
    assert "#25D366" in content, "Diagrama debe incluir WhatsApp (#25D366)"
    assert "#E1306C" in content, "Diagrama debe incluir Instagram (#E1306C)"
    assert "#6366F1" in content, "Diagrama debe incluir Web (#6366F1)"
    assert "TheIA Engine" in content or "theia-engine" in content.lower(), "Diagrama debe incluir TheIA Engine central"

    # Componente C: Bento Grid 2.0 de Capacidades Reales
    assert "home-bento" in content or "home-ui__bento" in content or "home-bento-grid" in content, (
        "index.html debe contener el Bento Grid 2.0 de Capacidades Reales"
    )
    # 4 capacidades del Bento 2.0
    assert ("Speed-to-Lead" in content or "<60s" in content or "&lt;60s" in content or "60 segundos" in content), "Bento debe incluir Speed-to-Lead <60s"
    assert "Pulse" in content, "Bento debe incluir TheIA Pulse"


def test_ac4_physical_design_tokens_and_site_cards_homologation():
    """HU-WEB-029 AC4: Cumplimiento de los 5 tokens de micro-detalle físico en site-cards.css."""
    assert SITE_CARDS_CSS.is_file(), "site-cards.css debe existir"
    css = SITE_CARDS_CSS.read_text(encoding="utf-8")

    # 1. Bisel especular superior
    assert "inset 0 1px 0 rgba(255, 255, 255, 0.09)" in css or "inset 0 1px 0 rgba(255,255,255,0.09)" in css, (
        "site-cards.css debe incluir el bisel especular superior inset 0 1px 0 rgba(255, 255, 255, 0.09)"
    )

    # 2. Elevación en 2 capas (--e1, --e2, --e3)
    assert "--e1" in css, "site-cards.css debe definir token de elevación --e1"
    assert "--e2" in css or "--e3" in css, "site-cards.css debe definir token de elevación --e2 o --e3"

    # 3. Curva Bezier de alta gama (cubic-bezier(0.16, 1, 0.3, 1))
    assert "cubic-bezier(0.16, 1, 0.3, 1)" in css or "cubic-bezier(0.16,1,0.3,1)" in css, (
        "site-cards.css debe utilizar la curva cubic-bezier(0.16, 1, 0.3, 1)"
    )

    # 4. Jerarquía de hairlines
    assert ("rgba(255, 255, 255, 0.08)" in css or "rgba(255,255,255,0.08)" in css or "--hairline-base" in css), (
        "site-cards.css debe definir la jerarquía de hairlines sutiles"
    )

    # 5. Focus ring accesible
    assert ":focus-visible" in css, "site-cards.css debe definir estados :focus-visible accesibles"
    assert "rgba(235, 202, 115, 0.7)" in css or "rgba(235,202,115,0.7)" in css or "--focus-ring" in css, (
        "site-cards.css debe configurar el anillo de foco accesible"
    )


def test_ac5_browser_interactive_elements_and_responsive(desktop_page, mobile_page):
    """HU-WEB-029 AC5: Interactividad en browser desktop y mobile, sin overflow y cero errores JS."""
    # Desktop test
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(300)

    # Verificar que los estilos de home-product-ui.css se hayan cargado
    bento = desktop_page.locator(".home-bento, .home-ui__bento, .home-bento-grid").first
    assert bento.is_visible(), "Bento Grid 2.0 debe ser visible en desktop"

    # Verificar interactividad del switch de reglas si existe botón/toggle
    rule_toggle = desktop_page.locator("[data-rule-toggle]").first
    if rule_toggle.is_visible():
        rule_toggle.click()
        desktop_page.wait_for_timeout(150)

    # Mobile test
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(300)

    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    client_w = mobile_page.evaluate("document.documentElement.clientWidth")
    assert scroll_w <= client_w, f"Desbordamiento horizontal en mobile: scrollWidth={scroll_w} > clientWidth={client_w}"

    js_errors = filtered_js_errors(mobile_page)
    assert len(js_errors) == 0, f"Errores de JS en consola: {js_errors}"
