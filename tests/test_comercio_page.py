"""Contratos de prueba automatizados para HU-WEB-023: Landing de vertical Comercio y Retail Local (/comercio.html).
"""
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
COMERCIO_PAGE = ROOT / "comercio.html"


def _visible_text(html):
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


def test_comercio_page_exists():
    assert COMERCIO_PAGE.is_file(), "comercio.html no existe en la raíz del repositorio"


def test_comercio_page_content_and_pillars():
    """AC1: Contenido específico de comercio y tiendas locales sin jerga ni testimonios falsos."""
    source = COMERCIO_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Vocabulario específico del sector
    required_keywords = [
        "tienda", "catálogo", "stock", "despacho",
        "productos", "pedidos"
    ]
    missing = [w for w in required_keywords if w not in visible]
    assert not missing, f"comercio.html no contiene vocabulario operativo clave del sector: {missing}"

    # Cero jerga startup
    forbidden_jargon = ["pipeline", "tenant", "lead scoring"]
    jargon_found = [w for w in forbidden_jargon if w in visible]
    assert not jargon_found, f"comercio.html contiene jerga startup prohibida: {jargon_found}"


def test_comercio_page_ctas_and_attribution():
    """AC3: CTAs y atribución correcta openTheiaChat('comercio')."""
    source = COMERCIO_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('comercio')" in source, "comercio.html no invoca openTheiaChat('comercio')"
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source, "comercio.html no tiene enlace a la demo de Google Calendar"


def test_comercio_page_loaded_in_scripts_and_sitemap():
    """AC5: Presente en sitemap.xml y llms.txt."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/comercio" in sitemap, "sitemap.xml no incluye https://theia.cl/comercio"

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "comercio" in llms.lower() or "retail" in llms.lower(), "llms.txt no menciona la solución para comercio y tiendas"
