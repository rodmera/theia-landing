"""Contratos de prueba automatizados para HU-WEB-042: Landing de Salud Pública (salud-publica.html).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SALUD_PUBLICA_PAGE = ROOT / "salud-publica.html"


def _visible_text(html: str) -> str:
    """Extrae texto visible (sin scripts, estilos, comentarios)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", " ", html)
    return html


def test_salud_publica_page_exists():
    """El archivo salud-publica.html debe existir en la raíz."""
    assert SALUD_PUBLICA_PAGE.is_file(), "salud-publica.html no existe en la raíz del repositorio"


def test_salud_publica_page_content_and_pillars():
    """AC1, AC2, AC3: Contenido específico de salud pública, Compra Ágil y módulos SOME."""
    source = SALUD_PUBLICA_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source).lower()

    # Vocabulario específico del sector y contratación pública
    required_keywords = [
        "salud pública", "pacientes", "confirmación", "recordatorios",
        "whatsapp", "sms", "contingencia", "some", "compra ágil",
        "78.474.636-4", "48 horas", "cesfam", "hospital"
    ]
    missing = [w for w in required_keywords if w not in visible]
    assert not missing, f"salud-publica.html no contiene vocabulario operativo clave: {missing}"

    # Cero jerga startup o clichés de IA
    forbidden_jargon = [
        "pipeline", "lead scoring", "revolucionario", "sin precedentes",
        "transformación digital", "de última generación", "al siguiente nivel",
        "desbloquea", "empodera"
    ]
    jargon_found = [w for w in forbidden_jargon if w in visible]
    assert not jargon_found, f"salud-publica.html contiene jerga prohibida: {jargon_found}"


def test_salud_publica_antislop_rules():
    """AC4: Cumplimiento de reglas antislop (sin em dashes, sin leyes específicas, sin precio fijo)."""
    source = SALUD_PUBLICA_PAGE.read_text(encoding="utf-8")
    visible = _visible_text(source)

    # Cero guiones largos
    assert "—" not in visible, "salud-publica.html contiene guiones largos (em dash)"

    # Sin citas a leyes específicas
    laws = re.findall(r"\bley\s*\d+\b", visible, re.IGNORECASE)
    assert not laws, f"salud-publica.html contiene citas a leyes específicas: {laws}"

    # Frase canónica de privacidad
    assert "cumplimiento de estándares de privacidad exigidos para salud" in visible.lower(), (
        "salud-publica.html debe incluir la redacción estándar de privacidad"
    )

    # Sin precio fijo
    forbidden_prices = ["$250.000", "$150.000", "$79.000"]
    for price in forbidden_prices:
        assert price not in visible, f"salud-publica.html no debe tener precio fijo ({price})"


def test_salud_publica_ctas_and_nav():
    """AC1, AC5: Enlaces correctos de navegación, demo y WhatsApp."""
    source = SALUD_PUBLICA_PAGE.read_text(encoding="utf-8")
    assert "https://calendar.app.google/ZDjEtqCXTJVxzi7bA" in source, (
        "salud-publica.html debe enlazar a la reunión técnica en Google Calendar"
    )
    assert "https://wa.me/12063858350" in source, "salud-publica.html debe enlazar a WhatsApp oficial"
    assert 'data-site-nav-page="salud-publica"' in source, "salud-publica.html debe tener data-site-nav-page"


def test_salud_publica_linked_in_sitemap_and_nav():
    """AC1: Enlazado desde sitemap.xml e index.html."""
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "https://theia.cl/salud-publica" in sitemap, "sitemap.xml debe incluir https://theia.cl/salud-publica"

    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'href="/salud-publica"' in index_html, "index.html debe enlazar a /salud-publica"
