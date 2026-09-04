"""Tests automatizados de calidad editorial, UX Writing y Wording de theia.cl.

Basado en las mejores prácticas de la industria:
- Nielsen Norman Group (NN/g): Scannability, eliminación de pleonasmos, meta-lenguaje y fluff.
- Torrey Podmajersky ("Strategic Writing for UX"): Consistencia de persona, concisión y ausencia de echoing.
- Sarah Richards ("Content Design"): Lenguaje llano, cohesión título-párrafo y eliminación de jerga inflada.
- Design System Oficial TheIA: Registro formal cercano para PYME chilena, tuteo consistente,
  integridad de naming de marca (TheIA, WhatsApp) y cero promesas vacías.
"""
import collections
from pathlib import Path
import re
from bs4 import BeautifulSoup
import pytest

ROOT = Path(__file__).resolve().parent.parent

# Archivos de marketing a auditar (excluyendo páginas puramente legales con plantillas legales formales)
MARKETING_HTML_FILES = [
    f for f in sorted(ROOT.glob("*.html"))
    if f.name not in {"privacidad.html", "terminos.html"}
]

# 1. Pleonasmos y tautologías comerciales en UI
PLEONASMS = [
    (r"\bcompletamente gratis\b", "usar 'gratis' o 'sin costo'"),
    (r"\btotalmente gratis\b", "usar 'gratis' o 'sin costo'"),
    (r"\btotalmente autom[aá]tico\b", "usar 'automático'"),
    (r"\bcompletamente autom[aá]tico\b", "usar 'automático'"),
    (r"\breintentar de nuevo\b", "usar 'reintentar' o 'intentar otra vez'"),
    (r"\bvolver a repetir\b", "usar 'repetir'"),
    (r"\brepetir de nuevo\b", "usar 'repetir'"),
    (r"\blapso de tiempo\b", "usar 'plazo' o 'tiempo'"),
    (r"\bper[ií]odo de tiempo\b", "usar 'período' o 'plazo'"),
    (r"\bresumen breve\b", "usar 'resumen'"),
    (r"\bresultado final\b", "usar 'resultado'"),
    (r"\bplanes a futuro\b", "usar 'planes'"),
    (r"\bsoluci[oó]n integral completa\b", "usar 'solución integral' o 'plataforma'"),
    (r"\binnovaci[oó]n novedosa\b", "usar 'innovación'"),
    (r"\bprever de antemano\b", "usar 'prever'"),
    (r"\bcolaborar conjuntamente\b", "usar 'colaborar'"),
    (r"\bbucle circular\b", "usar 'bucle' o 'ciclo'"),
]

# 2. Meta-lenguaje y redundancias obvias de interfaz
META_UI = [
    (r"\bhaz clic aqu[ií]\b", "usar verbo de acción directo en el botón o enlace"),
    (r"\bhaga clic aqu[ií]\b", "usar verbo de acción directo en el botón o enlace"),
    (r"\bclick aqu[ií]\b", "usar verbo de acción directo en el botón o enlace"),
    (r"\btoca el bot[oó]n para\b", "usar verbo de acción directo"),
    (r"\bpresiona el bot[oó]n para\b", "usar verbo de acción directo"),
    (r"\ba continuaci[oó]n te mostramos\b", "ir directo a la información"),
    (r"\ben la siguiente secci[oó]n te presentamos\b", "ir directo a la información"),
    (r"\ben esta secci[oó]n puedes ver\b", "ir directo a la información"),
]

# 3. Fluff, superlativos vacíos y anglicismos innecesarios
FLUFF_PATTERNS = [
    (r"\bde [uú]ltima generaci[oó]n\b", "especificar modelo o capacidad real"),
    (r"\bde vanguardia\b", "especificar beneficio técnico u operativo"),
    (r"\bde clase mundial\b", "especificar métricas o estándares concretos"),
    (r"\brevolucionari[ao]s?\b", "usar lenguaje sobrio y concreto"),
    (r"\bsin precedentes\b", "usar lenguaje sobrio y comprobable"),
    (r"\bdisruptiv[ao]s?\b", "usar lenguaje sobrio y concreto"),
    (r"\bparadigma\b", "usar lenguaje claro"),
    (r"\bhol[ií]stic[ao]s?\b", "usar lenguaje claro"),
    (r"\bsinergia\b", "usar lenguaje claro"),
    (r"\bcustomer-centric\b", "usar 'centrado en el cliente'"),
    (r"\bseamless\b", "usar 'fluido' o 'sin fricción'"),
    (r"\bgame-changer\b", "usar lenguaje sobrio"),
]

# 4. Inconsistencia de persona gramatical (ustedeo y voseo prohibidos en páginas de marketing)
USTEDEO_PATTERNS = [
    (r"\bsu negocio\b", "usar 'tu negocio' (tuteo estándar)"),
    (r"\bsus clientes\b", "usar 'tus clientes' (tuteo estándar)"),
    (r"\bsu empresa\b", "usar 'tu empresa' (tuteo estándar)"),
    (r"\busted\b", "usar tuteo consistente ('tú')"),
    (r"\bustedes\b", "usar tuteo / segunda persona adecuada"),
    (r"\bcomun[ií]quese\b", "usar 'comunícate'"),
]

VOSEO_PATTERNS = [
    (r"\btenés\b", "usar 'tienes'"),
    (r"\bpodés\b", "usar 'puedes'"),
    (r"\bquerés\b", "usar 'quieres'"),
    (r"\bsabés\b", "usar 'sabes'"),
    (r"\bhacés\b", "usar 'haces'"),
]

# Stop words en español para el análisis de repetición léxica (echoing)
SPANISH_STOP_WORDS = {
    "de", "la", "el", "en", "y", "a", "que", "los", "del", "se", "las", "por",
    "un", "para", "con", "no", "una", "su", "al", "es", "lo", "como", "más",
    "o", "pero", "sus", "le", "ha", "si", "sin", "sobre", "este", "ya",
    "entre", "cuando", "todo", "esta", "ser", "son", "dos", "también", "fue",
    "era", "muy", "hasta", "desde", "está", "mi", "porque", "qué", "solo",
    "han", "yo", "hay", "vez", "puede", "todos", "así", "nos", "ni", "parte",
    "tiene", "él", "uno", "donde", "bien", "tiempo", "mismo", "ese", "ahora",
    "cada", "e", "vida", "otro", "después", "te", "tu", "tus", "tuya", "tuyo",
    "tan", "tanto", "tanta", "estos", "estas", "theia", "agente", "agentes"
}


def _clean_visible_text(html_content: str) -> str:
    """Extrae únicamente el texto visible al usuario, omitiendo scripts, estilos y comentarios."""
    soup = BeautifulSoup(html_content, "html.parser")
    for elem in soup(["script", "style", "noscript", "svg"]):
        elem.decompose()
    return soup.get_text(" ", strip=True)


def test_wording_no_pleonasmos_ni_tautologias():
    """Valida la ausencia de pleonasmos y tautologías comerciales en el copy visible."""
    violations = []
    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if any(tag in line for tag in ["<script", "<style", "<!--"]):
                continue
            clean_line = re.sub(r"<[^>]+>", " ", line)
            clean_line = re.sub(r"\s+", " ", clean_line).strip()
            if not clean_line:
                continue

            for pattern, recommendation in PLEONASMS:
                match = re.search(pattern, clean_line, re.I)
                if match:
                    violations.append(
                        f"{file.name}:{idx} → Pleonasmo '{match.group()}' detectado. Sugerencia: {recommendation}"
                    )
    assert not violations, "Pleonasmos o tautologías encontrados en copy visible:\n" + "\n".join(violations)


def test_wording_no_fluff_superlativos_vacios_ni_anglicismos():
    """Valida la ausencia de superlativos vacíos, jerga inflada corporativa y anglicismos innecesarios."""
    violations = []
    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if any(tag in line for tag in ["<script", "<style", "<!--"]):
                continue
            clean_line = re.sub(r"<[^>]+>", " ", line)
            clean_line = re.sub(r"\s+", " ", clean_line).strip()
            if not clean_line:
                continue

            for pattern, recommendation in FLUFF_PATTERNS:
                match = re.search(pattern, clean_line, re.I)
                if match:
                    violations.append(
                        f"{file.name}:{idx} → Buzzword/Fluff '{match.group()}' detectado. Sugerencia: {recommendation}"
                    )
    assert not violations, "Fluff o buzzwords vacías encontradas en copy visible:\n" + "\n".join(violations)


def test_wording_tuteo_chileno_consistente_sin_ustedeo_ni_voseo():
    """Valida que todas las páginas de marketing empleen tuteo chileno estándar consistente."""
    violations = []
    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if any(tag in line for tag in ["<script", "<style", "<!--"]):
                continue
            clean_line = re.sub(r"<[^>]+>", " ", line)
            clean_line = re.sub(r"\s+", " ", clean_line).strip()
            if not clean_line:
                continue

            # Ustedeo
            for pattern, recommendation in USTEDEO_PATTERNS:
                match = re.search(pattern, clean_line, re.I)
                if match:
                    violations.append(
                        f"{file.name}:{idx} → Inconsistencia de persona (ustedeo) '{match.group()}'. Sugerencia: {recommendation}"
                    )

            # Voseo
            for pattern, recommendation in VOSEO_PATTERNS:
                match = re.search(pattern, clean_line, re.I)
                if match:
                    violations.append(
                        f"{file.name}:{idx} → Voseo no permitido en ecosistema '{match.group()}'. Sugerencia: {recommendation}"
                    )

    assert not violations, "Inconsistencias de tratamiento o voseo encontradas:\n" + "\n".join(violations)


def test_wording_no_meta_lenguaje_obvio_de_interfaz():
    """Valida que los botones y enlaces no usen meta-lenguaje obvio ('haz clic aquí')."""
    violations = []
    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if any(tag in line for tag in ["<script", "<style", "<!--"]):
                continue
            clean_line = re.sub(r"<[^>]+>", " ", line)
            clean_line = re.sub(r"\s+", " ", clean_line).strip()
            if not clean_line:
                continue

            for pattern, recommendation in META_UI:
                match = re.search(pattern, clean_line, re.I)
                if match:
                    violations.append(
                        f"{file.name}:{idx} → Meta-lenguaje redundante '{match.group()}'. Sugerencia: {recommendation}"
                    )

    assert not violations, "Meta-lenguaje obvio de interfaz encontrado:\n" + "\n".join(violations)


def test_wording_integridad_naming_de_marca_y_partners():
    """Valida la ortotipografía canónica de marcas (TheIA, WhatsApp, Instagram, Google Gemini, Ley 21.719)."""
    violations = []
    # Naming patterns que deben cumplirse estrictamente
    brand_checks = [
        (re.compile(r"\bTheia\b"), "TheIA"),
        (re.compile(r"\bTheIa\b"), "TheIA"),
        (re.compile(r"\bTHEIA\b(?!\.(?:CL|cl)|\s+SERVICIOS|\s+SpA)"), "TheIA"),
        (re.compile(r"\bWhatsapp\b"), "WhatsApp"),
        (re.compile(r"\bwhatsap\b", re.I), "WhatsApp"),
        (re.compile(r"\bwhats\b(?!\s+app)", re.I), "WhatsApp"),
        (re.compile(r"\bInstagram\b", re.I), "Instagram"),
        (re.compile(r"\bley\s+21\.?719\b"), "Ley 21.719"),
    ]

    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        lines = content.splitlines()
        in_json_ld = False
        for idx, line in enumerate(lines, 1):
            if '<script type="application/ld+json"' in line:
                in_json_ld = True
            if in_json_ld:
                if "</script>" in line:
                    in_json_ld = False
                continue
            if any(tag in line for tag in ["<script", "<style", "<!--", "href=", "src=", "http://", "https://"]):
                continue
            clean_line = re.sub(r"<[^>]+>", " ", line)
            clean_line = re.sub(r"\s+", " ", clean_line).strip()
            if not clean_line:
                continue

            for regex, expected in brand_checks:
                for match in regex.finditer(clean_line):
                    actual = match.group()
                    if actual != expected and actual.lower() == expected.lower():
                        violations.append(
                            f"{file.name}:{idx} → Naming '{actual}' debe ser '{expected}'"
                        )

    assert not violations, "Errores de naming de marcas detectados:\n" + "\n".join(violations)


def test_wording_no_echoing_reiterativo_en_parrafos():
    """Valida que en ningún párrafo <p> o ítem <li> se repita 3 o más veces la misma palabra clave."""
    violations = []
    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        for p in soup.find_all(["p", "li"]):
            # Omitir menús de navegación, pies de página o avisos legales
            if p.find_parents(["nav", "footer", "script", "style"]):
                continue
            text = p.get_text(" ", strip=True)
            if len(text) < 40 or "©" in text:
                continue

            words = [
                w.lower() for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", text)
                if w.lower() not in SPANISH_STOP_WORDS
            ]
            counts = collections.Counter(words)
            for word, count in counts.items():
                if count >= 3:
                    violations.append(
                        f"{file.name} → Palabra '{word}' repetida {count} veces en párrafo: \"{text[:80]}...\""
                    )

    assert not violations, "Echoing / repetición léxica excesiva en párrafos:\n" + "\n".join(violations)


def test_wording_cohesion_titulo_subtitulo_sin_tautologia():
    """Valida que los subtítulos (.section-sub) no sean un simple eco tautológico de sus títulos H2."""
    violations = []
    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        sections = soup.find_all("section")
        for s in sections:
            h2 = s.find("h2")
            if not h2:
                continue
            h2_text = h2.get_text(" ", strip=True)
            sub = s.find(class_=re.compile(r"section-sub"))
            if not sub:
                continue
            sub_text = sub.get_text(" ", strip=True)

            # Extraer palabras clave significativas
            h_words = {
                w.lower() for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", h2_text)
                if w.lower() not in SPANISH_STOP_WORDS
            }
            s_words = {
                w.lower() for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", sub_text)
                if w.lower() not in SPANISH_STOP_WORDS
            }

            # Si el subtítulo tiene menos de 4 palabras o no aporta información adicional
            if len(sub_text.split()) < 4:
                violations.append(
                    f"{file.name} [{s.get('id', 'section')}] → Subtítulo demasiado breve o vacío: '{sub_text}'"
                )

            # Si el subtítulo es idéntico al título
            if h2_text.strip().lower() == sub_text.strip().lower():
                violations.append(
                    f"{file.name} [{s.get('id', 'section')}] → Tautología total entre título y subtítulo: '{h2_text}'"
                )

    assert not violations, "Tautologías o falta de cohesión título-subtítulo:\n" + "\n".join(violations)
