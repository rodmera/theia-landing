"""Contratos de prueba automatizados para HU-WEB-025: Reencuadre de prueba social por industria (/casos.html).
"""
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
CASOS_PAGE = ROOT / "casos.html"


def _visible_text(html):
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_casos_page_exists():
    assert CASOS_PAGE.is_file(), "casos.html no existe en la raíz del repositorio"


def test_casos_page_content_and_industry_cases():
    """AC1: Reestructuración por industria (Salud, Servicios, Comercio, Automotriz) con casos de uso operativos sin testimonios falsos."""
    source = CASOS_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Industrias clave
    required_industries = [
        "salud & clínicas", "servicios & consultoría",
        "comercio & retail", "automotriz & talleres"
    ]
    missing = [w for w in required_industries if w not in visible]
    assert not missing, f"casos.html no contiene la reestructuración por industrias clave: {missing}"

    # Cero jerga startup
    forbidden_jargon = ["pipeline", "tenant", "lead scoring"]
    jargon_found = [w for w in forbidden_jargon if w in visible]
    assert not jargon_found, f"casos.html contiene jerga startup prohibida: {jargon_found}"


def test_casos_page_ctas_and_attribution():
    """AC4: CTAs y atribución correcta openTheiaChat('casos')."""
    source = CASOS_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('casos" in source or "openTheiaChat('casos-cta')" in source, "casos.html no invoca openTheiaChat('casos')"
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source, "casos.html no tiene enlace a la demo de Google Calendar"
