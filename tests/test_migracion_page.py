"""
Tests Playwright E2E para la Página de Migración de Datos hacia TheIA (HU-WEB-015).
Verifica:
- AC1: Contenido del proceso de migración (qué se trae, qué no, reversibilidad de 7 días, pasos).
- AC2: Sin promesas falsas ni mención a marcas de competidores en copy visible.
- AC3: Sección de preguntas frecuentes con respuestas claras (WhatsApp, equipo, tiempos).
- AC4: CTAs con atribución openTheiaChat('migracion'), navegación móvil (iPhone 14) y desktop, cero errores JS y cero overflow horizontal.
- AC5: Integración SEO y consistencia (sitemap.xml, llms.txt, conftest.py, footer).
"""
from pathlib import Path
import pytest
from conftest import BASE, ROOT, filtered_js_errors

MIGRACION_HTML = ROOT / "migracion.html"


def test_ac1_migracion_html_exists_and_declares_core_process():
    """HU-WEB-015 AC1: migracion.html existe y detalla entidades migrables, no migrables y reversibilidad."""
    assert MIGRACION_HTML.is_file(), "migracion.html no existe en la raíz"
    content = MIGRACION_HTML.read_text(encoding="utf-8")

    # 1. Títulos y encabezados
    assert "Tus datos se vienen contigo" in content
    assert "Sin perder tu historial comercial" in content

    # 2. Entidades que se migran
    assert "Contactos y Empresas" in content
    assert "Negocios y Etapas" in content
    assert "Notas y Tareas" in content

    # 3. Entidades que no se migran (con explicación transparente)
    assert "Conversaciones históricas" in content
    assert "WhatsApp y en Meta" in content

    # 4. Reversibilidad de 7 días
    assert "7 días de reversibilidad" in content or "7 Días de Reversibilidad" in content or "7 días completos" in content


def test_ac2_no_competitor_brands_in_visible_copy():
    """HU-WEB-015 AC2, AC5: Prohibido nombrar marcas específicas en copy visible (decisión estratégica 2026-07-29)."""
    content = MIGRACION_HTML.read_text(encoding="utf-8")
    
    # Términos genéricos requeridos
    assert "tu plataforma actual" in content or "donde tienes tus datos hoy" in content
    
    # Nombres de competidores que no deben figurar en copy visible
    competitor_brands = ["kommo", "hubspot", "zoho", "pipedrive", "manychat", "chatwoot"]
    # Limpiar comentarios y scripts para chequear solo copy visible
    import re
    body_text = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    body_text = re.sub(r"<script.*?>.*?</script>", "", body_text, flags=re.DOTALL)
    body_text = re.sub(r"<style.*?>.*?</style>", "", body_text, flags=re.DOTALL)
    
    body_lower = body_text.lower()
    for brand in competitor_brands:
        assert brand not in body_lower, f"Copy visible contiene marca de competidor '{brand}'"


def test_ac3_faqs_section_and_cross_links():
    """HU-WEB-015 AC3, AC5: Preguntas frecuentes clave y enlaces cruzados hacia /criterios y /crm."""
    content = MIGRACION_HTML.read_text(encoding="utf-8")

    assert "¿Qué pasa con mi número de WhatsApp actual?" in content
    assert "¿Cuánto demora todo el proceso de migración?" in content
    assert "¿Qué ocurre si me arrepiento después de migrar?" in content

    # Enlaces cruzados
    assert 'href="/criterios"' in content, "Falta enlace cruzado hacia /criterios"
    assert 'href="/crm"' in content, "Falta enlace cruzado hacia /crm"


def test_ac4_ctas_and_attribution():
    """HU-WEB-015 AC4: CTAs con atribución openTheiaChat('migracion')."""
    content = MIGRACION_HTML.read_text(encoding="utf-8")
    assert "openTheiaChat('migracion')" in content, "Falta atribución openTheiaChat('migracion') en CTA"


def test_ac4_mobile_viewport_layout_and_no_overflow(mobile_page):
    """HU-WEB-015 AC4: Responsividad móvil en iPhone 14 (390px), sin overflow ni errores JS."""
    mobile_page.goto(f"{BASE}/migracion.html", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    # 1. Título visible
    h1 = mobile_page.locator("h1")
    assert h1.is_visible(), "h1 debe ser visible en móvil"

    # 2. Cero overflow horizontal
    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    client_w = mobile_page.evaluate("document.documentElement.clientWidth")
    assert scroll_w <= client_w, f"Overflow horizontal detectado en /migracion: scrollWidth={scroll_w} > clientWidth={client_w}"

    # 3. Cero errores JS en consola
    assert len(filtered_js_errors(mobile_page)) == 0, "Errores JS detectados en /migracion"


def test_ac4_desktop_viewport_layout(desktop_page):
    """HU-WEB-015 AC4: Carga y layout correcto en desktop (1366x768)."""
    desktop_page.goto(f"{BASE}/migracion.html", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)

    h1 = desktop_page.locator("h1")
    assert h1.is_visible()
    assert len(filtered_js_errors(desktop_page)) == 0


def test_ac5_seo_and_footer_integration():
    """HU-WEB-015 AC5: Alta en sitemap.xml, llms.txt y presencia en footer."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/migracion" in sitemap

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "https://theia.cl/migracion" in llms

    content = MIGRACION_HTML.read_text(encoding="utf-8")
    assert 'href="/migracion"' in content, "Footer debe incluir enlace hacia /migracion"
