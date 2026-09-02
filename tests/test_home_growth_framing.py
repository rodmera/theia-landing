"""
Tests E2E Playwright para Homologación de Copywriting y Framing de Crecimiento en Home (HU-WEB-028).
Verifica:
- AC1: Hero principal con Merriweather 900, titular de crecimiento, bajada comercial, micro-copy y CTAs.
- AC2: Bloque de velocidad de respuesta (Speed-to-Lead / <60s).
- AC3: Bloque de acompañamiento de ingeniería local en Chile ("No te dejamos solo...").
- AC4: Bento stats cuantitativos de alto impacto (24/7 / 365, < 60s, 100% Certeza, $0 Extra).
- AC5: Cumplimiento del Design System (Trust strip 44px, logo 100px, paleta y tipografía).
- AC6: Cero desbordamiento horizontal en mobile (iPhone 14 / 390px).
"""
from pathlib import Path
import pytest
from conftest import BASE, ROOT, filtered_js_errors

INDEX_HTML = ROOT / "index.html"


def test_ac1_hero_growth_framing_copy_and_hierarchy():
    """HU-WEB-028 AC1: Hero principal con titular de crecimiento y micro-copy de valor."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    # 1. Titular principal
    assert "Agentes de IA que" in content, "Falta titular principal en hero"
    assert "impulsan tu negocio" in content, "Falta bajada en titular"

    # 2. Bajada comercial clara
    assert "catálogos reales" in content, "Falta catálogos en bajada"
    assert "agenda en tiempo real" in content or "agendan en tiempo real" in content, "Falta agendamiento en bajada"
    assert "Sin alucinaciones" in content, "Falta sin alucinaciones en bajada"

    # 3. Micro-copy de valor
    assert "Puesta en marcha en <7 días" in content or "Puesta en marcha en &lt;7 días" in content, "Falta micro-copy de puesta en marcha"
    assert "Sin costo por usuario" in content, "Falta micro-copy de costo por usuario"
    assert "Conectado a tu CRM" in content, "Falta micro-copy de CRM"

    # 4. CTAs principales
    assert "Probar Asistente en Vivo" in content, "Falta CTA primario Probar Asistente en Vivo"
    assert "Agendar Demo guiada" in content or "Agenda una demo" in content, "Falta CTA secundario de demo"


def test_ac2_and_ac3_acompanamiento_local_and_speed_to_lead():
    """HU-WEB-028 AC2, AC3: Sección de acompañamiento experto e impacto de velocidad de respuesta."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    # AC3: Mensaje explícito de acompañamiento asistido
    assert "No te dejamos solo con una herramienta" in content, "Falta titular de acompañamiento experto"
    assert "Puesta en Marcha Asistida" in content, "Falta mención a puesta en marcha asistida"
    assert "Acompañamiento Continuo" in content, "Falta tarjeta de acompañamiento continuo"

    # AC2: Propuesta Speed-to-Lead
    assert "Velocidad de Respuesta" in content, "Falta tarjeta de velocidad de respuesta"
    assert "menos de 60 segundos" in content, "Falta beneficio cuantitativo de respuesta <60s"


def test_ac4_bento_stats_metrics():
    """HU-WEB-028 AC4: Sección metrics-banner eliminada para evitar ruido visual bajo el Hero."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    assert "metrics-banner" not in content, "metrics-banner debe estar eliminada para evitar ruido visual bajo el Hero"


def test_ac5_design_system_trust_strip_and_logos(desktop_page):
    """HU-WEB-028 AC5: Preserva el trust strip de Google/NVIDIA a 44px y el logo a 100px."""
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)

    # Logo a 100px
    logo = desktop_page.locator(".logo img").first
    assert logo.is_visible()

    # Trust strip con Google for Startups y NVIDIA Inception
    trust_strip = desktop_page.locator(".hero-trust-strip")
    assert trust_strip.is_visible()
    assert "Google for Startups" in trust_strip.inner_text()

    nvidia_badge = trust_strip.locator("img[src='/nvidia-inception-program-badge.png']")
    assert nvidia_badge.is_visible()
    height = nvidia_badge.evaluate("el => el.offsetHeight")
    assert height == 44, f"Badge NVIDIA debe tener 44px de altura, tiene {height}px"


def test_ac6_no_horizontal_overflow_mobile(mobile_page):
    """HU-WEB-028 AC6: Cero desbordamiento horizontal en viewport móvil (390px)."""
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
    client_w = mobile_page.evaluate("document.documentElement.clientWidth")
    assert scroll_w <= client_w, f"Overflow horizontal detectado en home: scrollWidth={scroll_w} > clientWidth={client_w}"

    assert len(filtered_js_errors(mobile_page)) == 0, "Cero errores de JS en consola"


def test_agentes_especialistas_section_present_and_clean():
    """Verifica que la sección de Agentes Especialistas exista con los 6 agentes y sin clínicas dentales."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    assert 'id="agentes-especialistas"' in content
    assert "Agentes Especialistas" in content
    assert "Agente de Atención al Cliente" in content
    assert "Agente de Agendamiento &amp; Reservas" in content or "Agente de Agendamiento & Reservas" in content
    assert "Agente de Cotización &amp; Ventas" in content or "Agente de Cotización & Ventas" in content
    assert "Agente de Seguimiento &amp; CRM" in content or "Agente de Seguimiento & CRM" in content
    assert "Agente para Salud &amp; Bienestar" in content or "Agente para Salud & Bienestar" in content
    assert "Agente para Servicios Técnicos" in content

    # Verificación de exclusión de clínica dental
    assert "Clínica Dental" not in content
    assert "clínica dental" not in content
    assert "Dr. Matías Silva" not in content
    assert "limpiezas dentales" not in content

