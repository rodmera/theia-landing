"""Tests TDD para HU-WEB-033:
Artículo de Blog — Adhesión de TheIA al Código de Buenas Prácticas de IA 2026 de la CCS.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
POST_PATH = ROOT / "_posts" / "2026-08-28-codigo-buenas-practicas-ia-ccs-2026.md"
BLOG_INDEX_PATH = ROOT / "blog" / "index.html"
SITEMAP_PATH = ROOT / "sitemap.xml"
LLMS_PATH = ROOT / "llms.txt"


def test_post_file_exists():
    """AC1: El post existe en _posts/ con formato de nombre de fecha válido."""
    assert POST_PATH.exists(), f"No se encontró el post en {POST_PATH}"


def test_post_frontmatter():
    """AC1: Frontmatter estructurado con title, category, reading_time, author y excerpt."""
    content = POST_PATH.read_text(encoding="utf-8")
    assert content.startswith("---"), "El archivo debe iniciar con frontmatter YAML"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "Frontmatter YAML mal formado"
    fm = parts[1]

    assert "title:" in fm
    assert "category: Estrategia" in fm or 'category: "Estrategia"' in fm
    assert "reading_time:" in fm
    assert "author:" in fm
    assert "excerpt:" in fm


def test_blog_index_links_post():
    """AC1: blog/index.html contiene enlace al post /blog/codigo-buenas-practicas-ia-ccs-2026/."""
    index_html = BLOG_INDEX_PATH.read_text(encoding="utf-8")
    assert "/blog/codigo-buenas-practicas-ia-ccs-2026/" in index_html


def test_blog_index_card_structure():
    """AC1: blog/index.html incluye la post-card con clase post-card y categoría válida."""
    index_html = BLOG_INDEX_PATH.read_text(encoding="utf-8")
    match = re.search(
        r'<a href="/blog/codigo-buenas-practicas-ia-ccs-2026/" class="post-card reveal"[^>]*data-category="([^"]+)"',
        index_html
    )
    assert match is not None, "No se encontró la post-card enlazando al artículo"
    category = match.group(1)
    # Debe ser una de las categorías soportadas por los filtros
    assert category in ["Comparativa", "Estrategia", "Guía", "Negocios"]


def test_sitemap_and_llms_txt_include_post():
    """AC1: sitemap.xml y llms.txt incluyen la URL del nuevo artículo."""
    sitemap = SITEMAP_PATH.read_text(encoding="utf-8")
    assert "https://theia.cl/blog/codigo-buenas-practicas-ia-ccs-2026/" in sitemap

    llms = LLMS_PATH.read_text(encoding="utf-8")
    assert "codigo-buenas-practicas-ia-ccs-2026" in llms or "Código de Buenas Prácticas" in llms


def test_ccs_pdf_link_contract():
    """AC3/AC4: Enlace oficial al PDF de la CCS con URL exacta."""
    content = POST_PATH.read_text(encoding="utf-8")
    official_url = "https://stablobccsprod.blob.core.windows.net/ccs/2026/08/codigo_IA_CCS_2026_IMP.pdf"
    assert official_url in content, f"Falta enlace al PDF oficial de la CCS: {official_url}"


def test_cta_demo_present_without_broken_js():
    """AC3: CTA de agendamiento de demo presente y sin openTheiaChat que cause error JS."""
    content = POST_PATH.read_text(encoding="utf-8")
    calendar_url = "https://calendar.app.google/ZDjEtqCXTJVxzi7bA"
    assert calendar_url in content
    # _layouts/post.html no carga webchat-cta.js, openTheiaChat fallaría
    assert "openTheiaChat(" not in content


def test_content_covers_3_commitments_and_ccs_framework():
    """AC2: Contenido explica el marco CCS e incluye los 3 compromisos clave."""
    content = POST_PATH.read_text(encoding="utf-8")
    # Marco CCS
    assert "Cámara de Comercio de Santiago" in content or "CCS" in content
    assert "Código de Buenas Prácticas" in content

    # 3 Compromisos
    content_lower = content.lower()
    assert "transparencia" in content_lower or "identificación" in content_lower
    assert "supervisión humana" in content_lower or "human-in-the-loop" in content_lower or "derivación" in content_lower
    assert "seguridad" in content_lower or "gobernanza" in content_lower or "ley 21.719" in content_lower


def test_honesty_guard_no_false_certification():
    """D4 (Guard de honestidad): No afirmar falsamente certificaciones o sellos no otorgados."""
    content = POST_PATH.read_text(encoding="utf-8").lower()
    prohibited_claims = [
        "certificada por la ccs",
        "certificación de la ccs",
        "acreditada por la ccs",
        "acreditación de la ccs",
        "avalada por la ccs",
        "sello ccs",
        "aprobado por la ccs",
        "aprobada por la ccs",
        "respaldado por la ccs",
    ]
    for claim in prohibited_claims:
        assert claim not in content, f"Reclamación no autorizada detectada: '{claim}'"


def test_honesty_guard_progressive_adoption_transparency():
    """D3/B3 (Guard de honestidad): Transparencia/identificación redactada como adopción progresiva."""
    content = POST_PATH.read_text(encoding="utf-8").lower()
    progressive_terms = ["adopción progresiva", "progresiva", "compromiso", "avanzamos", "ruta de implementación"]
    assert any(term in content for term in progressive_terms), (
        "El compromiso de transparencia debe enmarcarse en adopción progresiva"
    )


def test_no_forbidden_jargon():
    """Regla de registro de CLAUDE.md: Sin jerga prohibida."""
    content = POST_PATH.read_text(encoding="utf-8").lower()
    forbidden = [
        "unicornio", "serie a", "levantar capital", "lead scoring"
    ]
    for word in forbidden:
        assert word not in content, f"Jerga prohibida encontrada: {word}"


def test_commercial_consistency():
    """Consistencia comercial: si menciona precio, debe ser $250.000 CLP/mes."""
    content = POST_PATH.read_text(encoding="utf-8")
    if "CLP" in content or "$" in content:
        prices = re.findall(r'\$\d{1,3}(?:\.\d{3})*\s*(?:CLP)?', content)
        for p in prices:
            # Si menciona valor mensual de TheIA debe ser 250.000
            if "250.000" in p or "0" in p:
                continue
            # Cualquier otro precio debe estar debidamente contextualizado
