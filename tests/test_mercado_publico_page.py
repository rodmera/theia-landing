"""Contratos de prueba automatizados para HU-WEB-043: Radar de Mercado Público (mercado-publico.html).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
MERCADO_PUBLICO_PAGE = ROOT / "mercado-publico.html"


def _visible_text(html: str) -> str:
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", " ", html)
    return html


def test_mercado_publico_page_exists():
    """El archivo mercado-publico.html debe existir en la raíz."""
    assert MERCADO_PUBLICO_PAGE.is_file(), "mercado-publico.html no existe en la raíz"


def test_mercado_publico_content_and_pillars():
    """AC1, AC2, AC3: Contenido del Radar, titular H1, pilares e inspector de bases."""
    source = MERCADO_PUBLICO_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Titular y subtítulo exactos
    assert "radar diario de compras ágiles y licitaciones de mercado público" in visible
    assert "detección automatizada de oportunidades" in visible
    assert "extracción de requisitos en las bases técnicas" in visible
    assert "verificación de admisibilidad" in visible

    # Pilares operativos
    assert "monitoreo diario" in visible or "monitoreo continuo" in visible
    assert "extracción de requisitos" in visible
    assert "catálogo de productos" in visible
    assert "alertas inmediatas" in visible and "whatsapp" in visible

    # Llamada orgánica al Pack Despegue
    assert "/auditoria-contactabilidad" in source
    assert "$50.000" in visible
    assert "pack despegue" in visible


def test_mercado_publico_antislop_rules():
    """AC4: Cumplimiento de reglas antislop (sin em dashes, sin leyes, sin clichés de IA)."""
    source = MERCADO_PUBLICO_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source)

    # Cero guiones largos
    assert "—" not in visible, "mercado-publico.html contiene guiones largos (em dash)"

    # Sin citas a leyes específicas
    laws = re.findall(r"\bley\s*\d+\b", visible, re.IGNORECASE)
    assert not laws, f"mercado-publico.html contiene citas a leyes específicas: {laws}"

    # Cero jerga startup o clichés de IA
    forbidden_jargon = [
        "revolucionario", "sin precedentes", "transformación digital",
        "de última generación", "al siguiente nivel", "desbloquea", "empodera"
    ]
    visible_lower = visible.lower()
    for word in forbidden_jargon:
        assert word not in visible_lower, f"mercado-publico.html contiene cliché: {word}"


def test_mercado_publico_sitemap_and_nav():
    """AC1, AC5: Registrado en sitemap y con contrato de navegación."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/mercado-publico" in sitemap, (
        "sitemap.xml debe incluir https://theia.cl/mercado-publico"
    )

    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'href="/mercado-publico"' in index_html, "index.html debe enlazar a /mercado-publico"

    source = MERCADO_PUBLICO_PAGE.read_text(encoding="utf-8")
    assert 'data-site-nav-page="mercado-publico"' in source
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source
    assert "https://wa.me/12063858350" in source
