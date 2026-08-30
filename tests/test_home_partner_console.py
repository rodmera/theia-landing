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

def test_hu_web_035_operational_console_three_stages_and_no_ai_mockup():
    """HU-WEB-035 AC1 & AC2: Consola operativa sobria de 3 etapas, tokens canónicos y sin mockup IA."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    hero_match = re.search(r'<section class="hero".*?</section>', content, re.DOTALL)
    assert hero_match is not None, "Debe existir la sección hero en index.html"
    hero = hero_match.group(0)

    # AC1: Sin canvas ni semáforos macOS ni emojis dentro de la consola
    assert "network-canvas" not in hero, "Hero no debe contener canvas de red de partículas"
    assert "#ef4444" not in hero, "Hero no debe usar semáforos rojos decorativos macOS"
    # Sin emojis en consola
    assert "🛡️" not in hero, "Consola no debe usar emoji de escudo"
    assert "🔒" not in hero, "Consola no debe usar emoji de candado"
    assert "⚡" not in hero, "Consola no debe usar emoji de rayo decorativo"

    # AC1: Tres etapas de la consola operativa
    assert "Etapa 1" in hero and "Consulta recibida" in hero, "Etapa 1 debe comunicar consulta recibida"
    assert "Etapa 2" in hero and "Reglas validadas" in hero, "Etapa 2 debe comunicar control de reglas validadas"
    assert "Etapa 3" in hero and "Oportunidad registrada" in hero, "Etapa 3 debe comunicar oportunidad registrada"
    assert "$185.000 CLP" in hero, "Etapa 2 debe mostrar precio de catálogo oficial $185.000 CLP"
    assert "Bloqueado" in hero, "Etapa 2 debe mostrar freno de descuentos bloqueado"
    assert "CRM" in hero and "Cotizado" in hero, "Etapa 3 debe mostrar trazabilidad CRM"

    # AC2: Tokens canónicos en consola (sin colores inventados #818cf8, #f59e0b)
    assert "#818cf8" not in hero, "Hero no debe usar color #818cf8 fuera de tokens"
    assert "#f59e0b" not in hero, "Hero no debe usar color #f59e0b fuera de tokens"
    # Canales oficiales presentes con sus hex de marca
    assert "#25D366" in hero, "Canal WhatsApp oficial debe estar presente (#25D366)"
    assert "#6366F1" in hero, "Canal Web oficial debe estar presente (#6366F1)"
    assert "#E1306C" in hero, "Canal Instagram oficial debe estar presente (#E1306C)"


@pytest.mark.parametrize("viewport_width", [961, 1024, 1100])
def test_hu_web_035_hero_console_responsive_range_961_to_1100(desktop_page, viewport_width):
    """HU-WEB-035 AC3: Consola operativa y cada fila interna sin desbordamiento ni recorte en 961-1100px."""
    desktop_page.set_viewport_size({"width": viewport_width, "height": 800})
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(250)

    # 1. Document scrollWidth <= clientWidth
    scroll_w = desktop_page.evaluate("document.documentElement.scrollWidth")
    client_w = desktop_page.evaluate("document.documentElement.clientWidth")
    assert scroll_w <= client_w, f"Desbordamiento horizontal en {viewport_width}px: scrollWidth={scroll_w} > clientWidth={client_w}"

    # 2. .hero-console scrollWidth <= clientWidth
    console = desktop_page.locator(".hero-console")
    assert console.is_visible(), f"Consola debe ser visible en {viewport_width}px"
    c_scroll = console.evaluate("el => el.scrollWidth")
    c_client = console.evaluate("el => el.clientWidth")
    assert c_scroll <= c_client, f".hero-console desborda en {viewport_width}px: scrollWidth={c_scroll} > clientWidth={c_client}"

    # 3. Cada fila interna relevante (.hero-console-header, .hero-stage-head, .hero-stage-row, .hero-console-footer)
    row_selectors = [".hero-console-header", ".hero-stage-head", ".hero-stage-row", ".hero-console-footer"]
    for selector in row_selectors:
        locators = desktop_page.locator(selector).all()
        assert len(locators) > 0, f"No se encontraron elementos para {selector}"
        for idx, el in enumerate(locators):
            r_scroll = el.evaluate("node => node.scrollWidth")
            r_client = el.evaluate("node => node.clientWidth")
            assert r_scroll <= r_client, (
                f"Elemento {selector}[{idx}] desborda en {viewport_width}px: scrollWidth={r_scroll} > clientWidth={r_client}"
            )

    js_errors = filtered_js_errors(desktop_page)
    assert len(js_errors) == 0, f"Errores de JS en consola en {viewport_width}px: {js_errors}"
    desktop_page.set_viewport_size({"width": 1366, "height": 768})
