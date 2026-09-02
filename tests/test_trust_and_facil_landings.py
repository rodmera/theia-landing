"""Pruebas de las landings de Centro de Confianza (HU-WEB-034) y Setup Fácil (HU-WEB-038)."""
from pathlib import Path
import pytest

from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
CONFIANZA_HTML = ROOT / "confianza.html"
FACIL_HTML = ROOT / "facil.html"


def test_confianza_html_structure_and_metadata():
    assert CONFIANZA_HTML.is_file(), "confianza.html debe existir"
    content = CONFIANZA_HTML.read_text(encoding="utf-8")

    assert "<title>Centro de Confianza & Legal" in content
    assert 'canonical" href="https://theia.cl/confianza"' in content
    assert "Términos de Servicio" in content
    assert "Política de Privacidad" in content
    assert "Anexo de Tratamiento de Datos" in content or "DPA" in content
    assert "Subprocesadores" in content

    # Subprocesadores verificados
    assert "Google Cloud Platform" in content
    assert "Meta Platforms" in content
    assert "Google Vertex AI" in content or "Anthropic" in content or "OpenAI" in content
    assert "Langfuse" in content


def test_facil_html_structure_and_metadata():
    assert FACIL_HTML.is_file(), "facil.html debe existir"
    content = FACIL_HTML.read_text(encoding="utf-8")

    assert "<title>Tu Agente de WhatsApp en 3 Audios" in content
    assert 'canonical" href="https://theia.cl/facil"' in content
    assert "3 Simples Pasos" in content or "3 Audios" in content
    assert "Clínica Dental" in content
    assert "Taller Mecánico" in content
    assert "Abogados" in content
    assert "btn-whatsapp" in content


def test_confianza_and_facil_design_system_conformance():
    for f in [CONFIANZA_HTML, FACIL_HTML]:
        content = f.read_text(encoding="utf-8")
        assert "Merriweather" in content
        assert "Plus Jakarta Sans" in content
        assert "drop-shadow(" not in content


def test_confianza_and_facil_navigation_in_browser(page):
    page.goto(f"{BASE}/confianza.html")
    page.wait_for_load_state("networkidle")
    assert page.is_visible("text=Centro de Confianza y Seguridad")
    assert page.is_visible("text=Proveedores de Infraestructura")

    page.goto(f"{BASE}/facil.html")
    page.wait_for_load_state("networkidle")
    assert page.is_visible("text=¿Cuánto tiempo pierdes respondiendo")
    assert page.is_visible("text=Tu IA Operativa en 3 Simples Pasos")
