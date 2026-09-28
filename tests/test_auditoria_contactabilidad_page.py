"""Contratos de prueba automatizados para HU-WEB-044: Pack Despegue (auditoria-contactabilidad.html).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
AUDITORIA_PAGE = ROOT / "auditoria-contactabilidad.html"
PRECIOS_PAGE = ROOT / "precios.html"
SALUD_PAGE = ROOT / "salud.html"
SALUD_PUBLICA_PAGE = ROOT / "salud-publica.html"


def _visible_text(html: str) -> str:
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", " ", html)
    return html


def test_auditoria_contactabilidad_page_exists():
    """El archivo auditoria-contactabilidad.html debe existir en la raíz."""
    assert AUDITORIA_PAGE.is_file(), "auditoria-contactabilidad.html no existe en la raíz"


def test_auditoria_contactabilidad_content_and_pillars():
    """AC1, AC2, AC3: Contenido del Pack Despegue, precio de $50.000, componentes A/B y límites."""
    source = AUDITORIA_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Titular y conceptos clave
    assert "pack despegue: diagnóstico de contactabilidad y análisis de mercado público" in visible
    assert "$50.000" in visible
    assert "100% abonable" in visible

    # Componente 1: Auditoría de canales y stress-test
    assert "stress-test" in visible or "contactabilidad" in visible
    assert "inasistencia" in visible or "no-show" in visible
    assert "horas" in visible and "ociosa" in visible

    # Componente 2: Análisis de Compra Ágil
    assert "compra ágil" in visible
    assert "mercado público" in visible
    assert "admisibilidad" in visible
    assert "borrador de propuesta" in visible

    # Límites estrictos de alcance
    assert "1 canal" in visible
    assert "72 horas" in visible
    assert "responsabilidad" in visible and "cliente" in visible


def test_auditoria_contactabilidad_antislop_rules():
    """AC4: Cumplimiento de reglas antislop (sin em dashes, sin leyes específicas, sin clichés)."""
    source = AUDITORIA_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source)

    # Cero guiones largos
    assert "—" not in visible, "auditoria-contactabilidad.html contiene guiones largos (em dash)"

    # Sin citas a leyes específicas
    laws = re.findall(r"\bley\s*\d+\b", visible, re.IGNORECASE)
    assert not laws, f"auditoria-contactabilidad.html contiene citas a leyes específicas: {laws}"

    # Cero jerga startup o clichés de IA
    forbidden_jargon = [
        "revolucionario", "sin precedentes", "transformación digital",
        "de última generación", "al siguiente nivel", "desbloquea", "empodera"
    ]
    visible_lower = visible.lower()
    for word in forbidden_jargon:
        assert word not in visible_lower, f"auditoria-contactabilidad.html contiene cliché: {word}"


def test_auditoria_contactabilidad_organic_callouts_in_pages():
    """AC3: Llamadas orgánicas en precios.html, salud.html y salud-publica.html."""
    assert "/auditoria-contactabilidad" in PRECIOS_PAGE.read_text(encoding="utf-8"), (
        "precios.html debe enlazar a /auditoria-contactabilidad"
    )
    assert "/auditoria-contactabilidad" in SALUD_PAGE.read_text(encoding="utf-8"), (
        "salud.html debe enlazar a /auditoria-contactabilidad"
    )
    assert "/auditoria-contactabilidad" in SALUD_PUBLICA_PAGE.read_text(encoding="utf-8"), (
        "salud-publica.html debe enlazar a /auditoria-contactabilidad"
    )


def test_auditoria_contactabilidad_sitemap_and_nav():
    """AC1, AC5: Registrado en sitemap y con contrato de navegación."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/auditoria-contactabilidad" in sitemap, (
        "sitemap.xml debe incluir https://theia.cl/auditoria-contactabilidad"
    )

    source = AUDITORIA_PAGE.read_text(encoding="utf-8")
    assert 'data-site-nav-page="auditoria-contactabilidad"' in source
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source
    assert "https://wa.me/12063858350" in source
