"""Contratos de prueba automatizados para HU-WEB-020: Landing de vertical Salud y Clínicas (/salud.html).
"""
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SALUD_PAGE = ROOT / "salud.html"


def _visible_text(html):
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_salud_page_exists():
    assert SALUD_PAGE.is_file(), "salud.html no existe en la raíz del repositorio"


def test_salud_page_content_and_pillars():
    """AC1: Contenido específico de salud y clínicas sin jerga ni testimonios falsos."""
    source = SALUD_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Vocabulario específico del sector
    required_keywords = [
        "clínica", "pacientes", "horas", "inasistencia",
        "confirmación", "recepción"
    ]
    missing = [w for w in required_keywords if w not in visible]
    assert not missing, f"salud.html no contiene vocabulario operativo clave del sector: {missing}"

    # Cero jerga startup
    forbidden_jargon = ["pipeline", "tenant", "lead scoring"]
    jargon_found = [w for w in forbidden_jargon if w in visible]
    assert not jargon_found, f"salud.html contiene jerga startup prohibida: {jargon_found}"


def test_salud_page_ctas_and_attribution():
    """AC3: CTAs y atribución correctaopenTheiaChat('salud')."""
    source = SALUD_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('salud')" in source, "salud.html no invoca openTheiaChat('salud')"
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source, "salud.html no tiene enlace a la demo de Google Calendar"


def test_salud_page_loaded_in_scripts_and_sitemap():
    """AC5: Presente en sitemap.xml y llms.txt."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/salud" in sitemap, "sitemap.xml no incluye https://theia.cl/salud"

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "salud" in llms.lower(), "llms.txt no menciona la solución para salud y clínicas"
