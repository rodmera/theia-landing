"""Contratos de prueba automatizados para HU-WEB-024: Página comparativa de alternativa sin cobro por asiento (/alternativa-crm.html).
"""
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
ALTERNATIVA_PAGE = ROOT / "alternativa-crm.html"


def _visible_text(html):
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_alternativa_page_exists():
    assert ALTERNATIVA_PAGE.is_file(), "alternativa-crm.html no existe en la raíz del repositorio"


def test_alternativa_page_content_and_pillars():
    """AC1: Contenido de comparación transparente de modelos sin nombrar competidores en copy público."""
    source = ALTERNATIVA_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Vocabulario de la comparativa
    required_keywords = [
        "asiento", "tarifa plana", "vendedores",
        "mensualidad", "módulo", "agenda"
    ]
    missing = [w for w in required_keywords if w not in visible]
    assert not missing, f"alternativa-crm.html no contiene vocabulario operativo clave: {missing}"

    # Cero jerga startup
    forbidden_jargon = ["pipeline", "tenant", "lead scoring"]
    jargon_found = [w for w in forbidden_jargon if w in visible]
    assert not jargon_found, f"alternativa-crm.html contiene jerga startup prohibida: {jargon_found}"


def test_alternativa_page_ctas_and_attribution():
    """AC3: CTAs y atribución correcta openTheiaChat('alternativa-crm')."""
    source = ALTERNATIVA_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('alternativa-crm')" in source, "alternativa-crm.html no invoca openTheiaChat('alternativa-crm')"
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source, "alternativa-crm.html no tiene enlace a la demo de Google Calendar"


def test_alternativa_page_loaded_in_scripts_and_sitemap():
    """AC5: Presente en sitemap.xml y llms.txt."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/alternativa-crm" in sitemap, "sitemap.xml no incluye https://theia.cl/alternativa-crm"

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "alternativa-crm" in llms.lower() or "sin cobro por asiento" in llms.lower(), "llms.txt no menciona la página comparativa alternativa sin cobro por asiento"
