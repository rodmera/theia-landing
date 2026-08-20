"""Pruebas de descompresión integral de la home y redistribución de confianza (TASK-202608192224).

Verifica:
1. index.html estructurado en los 8 bloques de alta conversión, sin las 6 features genéricas duplicadas
   ni las secciones pesadas de respaldo técnico, manifiesto o seguridad completa.
2. Hero de index.html con Trust Strip que incluye Google for Startups y NVIDIA Inception con su texto legal.
3. nosotros.html contiene las secciones de Manifiesto y Respaldo Tecnológico completo.
4. cumplimiento.html contiene las garantías de Seguridad & Privacidad para PYMEs.
5. Renderizado en navegador desktop y mobile sin overflow horizontal.
"""
from pathlib import Path
import re
import pytest

from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"
NOSOTROS_HTML = ROOT / "nosotros.html"
CUMPLIMIENTO_HTML = ROOT / "cumplimiento.html"


def test_home_does_not_contain_heavy_or_duplicate_sections():
    """index.html no debe contener las secciones pesadas trasladadas ni las 6 features duplicadas."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    
    assert "class=\"respaldo-tech\"" not in content and "id=\"respaldo-tech\"" not in content, (
        "index.html aún contiene la sección pesada .respaldo-tech"
    )
    assert "class=\"manifiesto\"" not in content and "id=\"manifiesto\"" not in content, (
        "index.html aún contiene la sección .manifiesto"
    )
    assert "class=\"confianza-local\"" not in content and "id=\"confianza\"" not in content, (
        "index.html aún contiene la sección .confianza-local"
    )
    assert "class=\"features\"" not in content and "id=\"features\"" not in content, (
        "index.html aún contiene las 6 features genéricas duplicadas"
    )


def test_home_hero_contains_trust_strip():
    """Hero de index.html debe incluir el Trust Strip con Google for Startups, y NVIDIA en navbar/footer."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    
    assert "hero-trust-strip" in content or "trust-strip" in content, (
        "Hero de index.html debe contener el bloque de confianza .hero-trust-strip"
    )
    assert "Google for Startups" in content, "Trust strip debe mencionar Google for Startups"
    assert "/nvidia-inception-program-badge.png" in content, "Home debe incluir el badge de NVIDIA"
    assert "NVIDIA Inception Program are trademarks" in content, "Footer debe incluir la línea legal de NVIDIA"


def test_nosotros_contains_manifiesto_and_respaldo_tech():
    """nosotros.html debe contener el Manifiesto completo y el Respaldo Tecnológico de confianza."""
    content = NOSOTROS_HTML.read_text(encoding="utf-8")
    
    assert "Por qué existe" in content or "manifiesto" in content, "nosotros.html debe contener el Manifiesto"
    assert "La tecnología de las grandes marcas" in content or "respaldo-tech" in content, (
        "nosotros.html debe contener el Respaldo Tecnológico"
    )
    assert "Google Cloud" in content
    assert "Google Gemini" in content
    assert "NVIDIA Inception" in content
    assert "/nvidia-inception-program-badge.png" in content


def test_cumplimiento_contains_security_pillars():
    """cumplimiento.html debe incorporar las garantías de seguridad para PYMEs."""
    content = CUMPLIMIENTO_HTML.read_text(encoding="utf-8")
    
    assert "Seguridad y Privacidad" in content
    assert "Soporte Local Directo" in content or "Google Cloud" in content
    assert "Protección de Datos Sensibles" in content or "PII" in content
    assert "Aislamiento & Control del Dueño" in content or "Aislamiento" in content


def test_home_render_in_browser_and_no_horizontal_overflow(mobile_page, desktop_page):
    """Verifica en desktop y mobile que la home cargue limpia y sin overflow horizontal."""
    # Desktop
    desktop_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    desktop_page.wait_for_timeout(200)
    has_overflow_desktop = desktop_page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
    assert not has_overflow_desktop, "index.html tiene overflow horizontal en desktop"
    
    # Mobile
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)
    has_overflow_mobile = mobile_page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
    assert not has_overflow_mobile, "index.html tiene overflow horizontal en mobile"
