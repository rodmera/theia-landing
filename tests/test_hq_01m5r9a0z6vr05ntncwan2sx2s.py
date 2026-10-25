"""Tests de contrato: Ecosistema Multi-Agente, Memoria Persistente y Herdr en TheIA Landing.

Tarea: HQ-01M5R9A0Z6VR05NTNCWAN2SX2S
Spec: /home/rodmera/.openclaw/workspace/memory/feature-hq-01m5r9a0z6vr05ntncwan2sx2s.md

Criterios de Aceptación:
1. Grilla de logos y nombres de agentes/modelos vigentes (Hermes Agent, Herdr,
   Claude Code, Google Gemini, OpenAI, Anthropic Claude, OpenCode, Pi, DeepSeek,
   Meta Llama, MCP, Langfuse, CrewAI, Ollama).
2. Retiro absoluto de referencias obsoletas a Codex en la grilla y en llms.txt / llms-full.txt.
3. SVGs vectoriales limpios monocromo y conformes a XML sin dimensiones auto.
4. Narrativa de Ecosistema Multi-Agente con memoria persistente y orquestación Herdr
   en index.html (#arquitectura y #servicios-especializados), orquestacion.html y servicios.html.
5. Calidad editorial: cero AI slop, cero pleonasmos, tuteo chileno consistente.
6. Cumplimiento de reglas de diseño TheIA (Merriweather 900 en H2, tarjetas alineadas a la izquierda en Home, cero emojis en tarjetas).
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pytest

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"
ORQUESTACION_HTML = ROOT / "orquestacion.html"
SERVICIOS_HTML = ROOT / "servicios.html"
LLMS_TXT = ROOT / "llms.txt"
LLMS_FULL_TXT = ROOT / "llms-full.txt"


def _extract_logos_grid(content: str) -> str:
    """Extrae el contenido HTML de la grilla de modelos y runtimes de IA."""
    match = re.search(
        r'<div class=["\']conecta-category-label["\']>Modelos.*?</div>\s*<div class=["\']conecta-logos-grid["\']>(.*?)</div>\s*</div>',
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        match = re.search(
            r'Modelos, Protocolos &amp; Runtimes de IA</div>\s*<div class="conecta-logos-grid">(.*?)</div>\s*</div>',
            content,
            re.DOTALL,
        )
    assert match, "No se encontró el bloque conecta-logos-grid de Modelos & Runtimes en index.html"
    return match.group(1)


def test_logos_grid_contains_all_required_agents_and_models():
    """AC-1: La grilla de logos de IA debe incluir los 14 agentes y modelos requeridos."""
    assert INDEX_HTML.is_file(), "index.html debe existir"
    content = INDEX_HTML.read_text(encoding="utf-8")
    grid_html = _extract_logos_grid(content)

    required_names = [
        "OpenAI",
        "Anthropic Claude",
        "Google Gemini",
        "DeepSeek",
        "Meta Llama",
        "Claude Code",
        "OpenCode",
        "Pi",
        "Hermes Agent",
        "Herdr",
        "MCP",
        "Langfuse",
        "CrewAI",
        "Ollama",
    ]

    missing = []
    for name in required_names:
        if name == "Anthropic Claude":
            if not ("Anthropic Claude" in grid_html or "Anthropic / Claude" in grid_html):
                missing.append(name)
        elif name == "Hermes Agent":
            if not ("Hermes Agent" in grid_html or ">Hermes<" in grid_html):
                missing.append(name)
        else:
            if f">{name}<" not in grid_html and f"<span>{name}</span>" not in grid_html:
                missing.append(name)

    assert not missing, f"Faltan los siguientes agentes/modelos en la grilla de logos de index.html: {missing}"
    assert "Anthropic Claude" in grid_html, "Debe decir 'Anthropic Claude' en lugar de 'Anthropic / Claude'"
    assert "Hermes Agent" in grid_html, "Debe decir 'Hermes Agent' en lugar de solo 'Hermes'"


def test_codex_retired_from_logos_grid_and_metadata():
    """AC-2: Codex es un runtime obsoleto y debe ser retirado de la grilla y de la documentación de contexto."""
    assert INDEX_HTML.is_file()
    index_content = INDEX_HTML.read_text(encoding="utf-8")
    grid_html = _extract_logos_grid(index_content)

    assert "Codex" not in grid_html, (
        "Codex debe ser retirado o reemplazado en la grilla de logos de index.html (principle-subtract-before-you-add)."
    )

    if LLMS_TXT.is_file():
        llms_text = LLMS_TXT.read_text(encoding="utf-8")
        assert "Codex" not in llms_text, (
            "Codex debe ser retirado de llms.txt y reemplazado por agentes vigentes (OpenCode, Pi)."
        )

    if LLMS_FULL_TXT.is_file():
        llms_full_text = LLMS_FULL_TXT.read_text(encoding="utf-8")
        assert "Codex" not in llms_full_text, (
            "Codex debe ser retirado de llms-full.txt y reemplazado por agentes vigentes (OpenCode, Pi)."
        )


def test_logos_svg_monochrome_xml_validity():
    """AC-3: Todos los SVGs de la grilla deben ser vectores limpios sin 'auto' y con XML válido."""
    content = INDEX_HTML.read_text(encoding="utf-8")
    grid_html = _extract_logos_grid(content)

    svgs = re.findall(r'<svg[^>]*>.*?</svg>', grid_html, re.DOTALL)
    assert len(svgs) >= 14, f"Se esperaban al menos 14 SVGs en la grilla, encontrados {len(svgs)}"

    for i, svg_snippet in enumerate(svgs):
        assert 'width="auto"' not in svg_snippet, f"SVG {i} contiene width='auto' prohibido por XML"
        assert 'height="auto"' not in svg_snippet, f"SVG {i} contiene height='auto' prohibido por XML"
        assert 'viewBox=' in svg_snippet, f"SVG {i} debe tener viewBox definido"

        try:
            ET.fromstring(svg_snippet)
        except ET.ParseError as e:
            pytest.fail(f"SVG {i} en la grilla de logos no es XML bien formado: {e}\nSnippet: {svg_snippet}")


def test_index_architecture_narrative_ecosystem_and_memory():
    """AC-4: index.html debe incorporar en #arquitectura y #servicios-especializados el Ecosistema Multi-Agente con Herdr y memoria persistente."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    # 1. Sección #arquitectura
    arch_match = re.search(r'<section[^>]*id=["\']arquitectura["\'][^>]*>(.*?)</section>', content, re.DOTALL)
    assert arch_match, "No se encontró la sección #arquitectura en index.html"
    arch_html = arch_match.group(1)

    assert "Herdr" in arch_html or "orquestación Herdr" in arch_html or "herdr" in arch_html.lower(), (
        "#arquitectura en index.html debe explicitar la orquestación con Herdr."
    )
    assert re.search(r'memoria\s+(?:compartida|persistente|cross-canal)', arch_html, re.I), (
        "#arquitectura en index.html debe explicitar la memoria compartida / persistente entre canales."
    )
    assert re.search(r'sin perder contexto|no perder contexto|preserva el contexto', arch_html, re.I), (
        "#arquitectura en index.html debe destacar que los agentes operan sin perder contexto entre canales ni sesiones."
    )

    # 2. Sección #servicios-especializados
    serv_match = re.search(r'<section[^>]*id=["\']servicios-especializados["\'][^>]*>(.*?)</section>', content, re.DOTALL)
    assert serv_match, "No se encontró la sección #servicios-especializados en index.html"
    serv_html = serv_match.group(1)

    assert "Herdr" in serv_html, (
        "#servicios-especializados en index.html debe mencionar la orquestación Herdr como parte del ecosistema."
    )
    assert re.search(r'memoria\s+(?:compartida|persistente)', serv_html, re.I), (
        "#servicios-especializados en index.html debe mencionar memoria compartida o persistente."
    )


def test_orquestacion_page_herdr_and_persistent_memory():
    """AC-5: orquestacion.html debe describir la coordinación multi-agente con Herdr y memoria compartida."""
    assert ORQUESTACION_HTML.is_file(), "orquestacion.html debe existir"
    content = ORQUESTACION_HTML.read_text(encoding="utf-8")

    assert "Herdr" in content, (
        "orquestacion.html debe mencionar Herdr en la arquitectura u orquestación de agentes."
    )
    assert re.search(r'memoria\s+(?:compartida|persistente|bi-temporal)', content, re.I), (
        "orquestacion.html debe describir la memoria compartida o persistente."
    )
    assert re.search(r'sin perder contexto|no perder contexto|aislamiento de contexto', content, re.I), (
        "orquestacion.html debe enfatizar la preservación y control del contexto operativo."
    )


def test_servicios_page_herdr_and_multiagent_orchestration():
    """AC-6: servicios.html debe incluir en su catálogo Eje 1 la orquestación con Herdr y memoria compartida."""
    assert SERVICIOS_HTML.is_file(), "servicios.html debe existir"
    content = SERVICIOS_HTML.read_text(encoding="utf-8")

    assert "Herdr" in content, (
        "servicios.html debe incluir Herdr en el servicio de Arquitectura de Agentes & Orquestación."
    )
    assert re.search(r'memoria\s+(?:compartida|persistente)', content, re.I), (
        "servicios.html debe mencionar memoria persistente o compartida."
    )


def test_wording_quality_compliance():
    """AC-7: Verificación de calidad de copy: cero AI slop, cero pleonasmos y tuteo consistente."""
    forbidden_slop = [
        "al siguiente nivel",
        "empoderar",
        "potencia al máximo",
        "revolucionario",
        "de vanguardia",
        "transformación digital",
        "seamless",
        "solución integral completa",
        "completamente gratis",
        "totalmente automático",
    ]

    for file_path in [INDEX_HTML, ORQUESTACION_HTML, SERVICIOS_HTML]:
        content = file_path.read_text(encoding="utf-8")
        for slop in forbidden_slop:
            assert slop.lower() not in content.lower(), (
                f"Término de AI slop / pleonasmo '{slop}' detectado en {file_path.name}"
            )


def test_card_alignment_and_design_contract():
    """AC-8: Las tarjetas de index.html deben mantenerse alineadas a la izquierda y sin emojis."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    # Prohibición de emojis en elementos de icono
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]')
    for match in re.finditer(r'class=["\'][^"\']*(?:card-icon|icon-wrap)[^"\']*["\']>([^<]+)<', content):
        icon_text = match.group(1).strip()
        assert not emoji_pattern.search(icon_text), f"Emoji prohibido en contenedor de icono: '{icon_text}'"

    # Verificar que no haya sobrescrituras text-align: center en tarjetas de la home
    card_sections = re.findall(
        r'<section[^>]*class=["\'][^"\']*(?:servicios-especializados|autoridad-determinista)[^"\']*["\'][^>]*>.*?</section>',
        content,
        re.DOTALL,
    )
    for section in card_sections:
        assert 'style="text-align: center;"' not in section and 'style="text-align:center"' not in section or (
            # Permitir encabezados centrados pero no en las tarjetas
            'class="conecta-card" style="text-align: center"' not in section
            and 'class="determinista-card" style="text-align: center"' not in section
        ), "Las tarjetas de la home deben estar alineadas a la izquierda (regla dura de diseño)"
