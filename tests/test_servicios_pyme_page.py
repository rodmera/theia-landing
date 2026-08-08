"""Contratos de prueba automatizados para HU-WEB-021: Landing de vertical Servicios y Consultoría (/servicios-pyme.html).
"""
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SERVICIOS_PAGE = ROOT / "servicios-pyme.html"


def _visible_text(html):
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_servicios_pyme_page_exists():
    assert SERVICIOS_PAGE.is_file(), "servicios-pyme.html no existe en la raíz del repositorio"


def test_servicios_pyme_page_content_and_pillars():
    """AC1: Contenido específico de servicios B2B y consultoría sin jerga ni testimonios falsos."""
    source = SERVICIOS_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Vocabulario específico del sector
    required_keywords = [
        "servicios", "prospectos", "cotizaciones", "reuniones",
        "seguimiento", "equipo"
    ]
    missing = [w for w in required_keywords if w not in visible]
    assert not missing, f"servicios-pyme.html no contiene vocabulario operativo clave del sector: {missing}"

    # Cero jerga startup
    forbidden_jargon = ["pipeline", "tenant", "lead scoring"]
    jargon_found = [w for w in forbidden_jargon if w in visible]
    assert not jargon_found, f"servicios-pyme.html contiene jerga startup prohibida: {jargon_found}"


def test_servicios_pyme_page_ctas_and_attribution():
    """AC3: CTAs y atribución correcta openTheiaChat('servicios-pyme')."""
    source = SERVICIOS_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('servicios-pyme')" in source, "servicios-pyme.html no invoca openTheiaChat('servicios-pyme')"
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source, "servicios-pyme.html no tiene enlace a la demo de Google Calendar"


def test_servicios_pyme_page_loaded_in_scripts_and_sitemap():
    """AC5: Presente en sitemap.xml y llms.txt."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/servicios-pyme" in sitemap, "sitemap.xml no incluye https://theia.cl/servicios-pyme"

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "servicios-pyme" in llms.lower() or "servicios & consultoría" in llms.lower(), "llms.txt no menciona la solución para empresas de servicios y consultoría"
