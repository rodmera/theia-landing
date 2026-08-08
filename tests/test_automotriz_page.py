"""Contratos de prueba automatizados para HU-WEB-022: Landing de vertical Automotriz y Talleres (/automotriz.html).
"""
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
AUTOMOTRIZ_PAGE = ROOT / "automotriz.html"


def _visible_text(html):
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_automotriz_page_exists():
    assert AUTOMOTRIZ_PAGE.is_file(), "automotriz.html no existe en la raíz del repositorio"


def test_automotriz_page_content_and_pillars():
    """AC1: Contenido específico de automotriz y talleres sin jerga ni testimonios falsos."""
    source = AUTOMOTRIZ_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Vocabulario específico del sector
    required_keywords = [
        "taller", "vehículo", "mantención", "repuestos",
        "recepción", "retiro"
    ]
    missing = [w for w in required_keywords if w not in visible]
    assert not missing, f"automotriz.html no contiene vocabulario operativo clave del sector: {missing}"

    # Cero jerga startup
    forbidden_jargon = ["pipeline", "tenant", "lead scoring"]
    jargon_found = [w for w in forbidden_jargon if w in visible]
    assert not jargon_found, f"automotriz.html contiene jerga startup prohibida: {jargon_found}"


def test_automotriz_page_ctas_and_attribution():
    """AC3: CTAs y atribución correcta openTheiaChat('automotriz')."""
    source = AUTOMOTRIZ_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('automotriz')" in source, "automotriz.html no invoca openTheiaChat('automotriz')"
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source, "automotriz.html no tiene enlace a la demo de Google Calendar"


def test_automotriz_page_loaded_in_scripts_and_sitemap():
    """AC5: Presente en sitemap.xml y llms.txt."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/automotriz" in sitemap, "sitemap.xml no incluye https://theia.cl/automotriz"

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "automotriz" in llms.lower() or "talleres" in llms.lower(), "llms.txt no menciona la solución para automotriz y talleres"
