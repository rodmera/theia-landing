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

# 5. AI Slop, clichés sintéticos de LLMs y fórmulas vacías de marketing
AI_SLOP_PATTERNS = [
    (r"\bal siguiente nivel\b", "usar resultado u objetivo operativo concreto"),
    (r"\bdesbloquea(?:r|s)? (?:el|tu)?\s*potencial\b", "especificar capacidad operativa real"),
    (r"\bdesata(?:r|s)? (?:el|tu)?\s*potencial\b", "especificar capacidad operativa real"),
    (r"\bempodera(?:r|s)?\b", "usar verbos concretos ('gestiona', 'organiza', 'decide')"),
    (r"\bimagina un mundo\b", "ir directo al problema de la PYME"),
    (r"\ben el mundo (?:actual|de hoy|vertiginoso|din[aá]mico)\b", "ir directo a la realidad comercial"),
    (r"\bel futuro (?:es hoy|ya est[aá] aqu[ií])\b", "especificar qué hace la herramienta hoy"),
    (r"\bes importante (?:destacar|se[ñn]alar|mencionar)\b", "eliminar muletilla e ir directo al dato"),
    (r"\bvale la pena (?:se[ñn]alar|destacar|mencionar)\b", "eliminar muletilla e ir directo al dato"),
    (r"\bes crucial (?:comprender|entender|destacar)\b", "eliminar muletilla e ir directo al dato"),
    (r"\bdise[ñn]ado meticulosamente\b", "especificar arquitectura y estándares reales"),
    (r"\bun tapiz de\b", "cliché de traducción de LLM"),
    (r"\bun faro de\b", "metáfora vacía de LLM"),
    (r"\bun catalizador\b", "metáfora vacía de LLM"),
    (r"\bun testimonio de\b", "cliché de traducción de LLM"),
    (r"\bla soluci[oó]n definitiva\b", "afirmación hiperbólica vacía"),
    (r"\btodo lo que necesitas y m[aá]s\b", "especificar módulos y funciones concretas"),
    (r"\bsatisfacer todas tus necesidades\b", "especificar alcance real"),
    (r"\bexperiencia inigualable\b", "superlativo vacío"),
    (r"\bpotencia al m[aá]ximo\b", "especificar impacto concreto"),
    (r"\bmaximiza tus resultados\b", "especificar métrica o impacto"),
    (r"\bun viaje hacia\b", "metáfora vacía de LLM"),
    (r"\ben conclusi[oó]n\b", "cierre escolar innecesario"),
    (r"\ben definitiva\b", "muletilla de relleno"),
    (r"\binteligencia artificial avanzada\b", "especificar modelo o capacidad concreta"),
    (r"\bia avanzada\b", "especificar modelo o capacidad concreta"),
    (r"\btransformaci[oó]n digital\b", "especificar procesos o sistemas concretos"),
    (r"\bsoluciones a la medida\b", "especificar servicios de ingeniería o integración"),
    (r"\bf[aá]cil y r[aá]pido\b", "especificar tiempos reales de respuesta o setup"),
    (r"\br[aá]pido y sencillo\b", "especificar tiempos reales de respuesta o setup"),
    (r"\bl[ií]der en el mercado\b", "afirmación no demostrada"),
    (r"\bpioner[ao]s? en\b", "afirmación no demostrada"),
    (r"\bmultiplica tus ventas\b", "afirmación hiperbólica sin evidencia"),
    (r"\bde la noche a la ma[ñn]ana\b", "afirmación irreal"),
    (r"\bingresos pasivos\b", "lenguaje engañoso de marketing"),
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


def test_wording_no_ai_slop_ni_cliches_genericos():
    """Valida la ausencia de fórmulas trilladas de IA (AI slop) y clichés de marketing vacíos."""
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

            for pattern, recommendation in AI_SLOP_PATTERNS:
                match = re.search(pattern, clean_line, re.I)
                if match:
                    violations.append(
                        f"{file.name}:{idx} → AI Slop / Cliché '{match.group()}' detectado. Sugerencia: {recommendation}"
                    )
    assert not violations, "Fórmulas de AI slop o clichés genéricos encontrados en copy visible:\n" + "\n".join(violations)


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
        content_clean = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", content, flags=re.S | re.I)
        items = re.findall(r"<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>", content_clean, flags=re.S | re.I)
        for item in items:
            text = re.sub(r"<[^>]+>", " ", item)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 40 or "©" in text:
                continue

            words = [
                w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", text.lower())
                if w not in SPANISH_STOP_WORDS
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
        sections = re.findall(r"<section[^>]*>(.*?)</section>", content, flags=re.S | re.I)
        for sec in sections:
            h2_match = re.search(r"<h2[^>]*>(.*?)</h2>", sec, flags=re.S | re.I)
            sub_match = re.search(r"class=['\"][^'\"]*section-sub[^'\"]*['\"][^>]*>(.*?)</", sec, flags=re.S | re.I)
            if not h2_match or not sub_match:
                continue

            h2_text = re.sub(r"<[^>]+>", " ", h2_match.group(1))
            h2_text = re.sub(r"\s+", " ", h2_text).strip()

            sub_text = re.sub(r"<[^>]+>", " ", sub_match.group(1))
            sub_text = re.sub(r"\s+", " ", sub_text).strip()

            if len(sub_text.split()) < 4:
                violations.append(
                    f"{file.name} → Subtítulo demasiado breve o vacío: '{sub_text}'"
                )

            if h2_text.strip().lower() == sub_text.strip().lower():
                violations.append(
                    f"{file.name} → Tautología total entre título y subtítulo: '{h2_text}'"
                )

    assert not violations, "Tautologías o falta de cohesión título-subtítulo:\n" + "\n".join(violations)


def test_wording_no_consecutive_headings_echo():
    """Valida que no exista 'Heading Stacking Echo': dos titulares contiguos (H1->H2 o H2->H2)
    no pueden arrancar con la misma palabra clave ni compartir el 60% de sus términos de contenido."""
    violations = []
    heading_stop_words = SPANISH_STOP_WORDS | {
        "de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "por", "con",
        "tu", "tus", "su", "sus", "que", "te", "o", "al", "del", "no", "si", "más"
    }

    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        content_clean = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", content, flags=re.S | re.I)

        headings = []
        for m in re.finditer(r"<(h[12])\b[^>]*>(.*?)</\1>", content_clean, flags=re.S | re.I):
            txt = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
            txt = re.sub(r"\s+", " ", txt)
            words = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", txt.lower()) if w not in heading_stop_words]
            headings.append((m.group(1), txt, words))

        for i in range(len(headings) - 1):
            t1, txt1, w1 = headings[i]
            t2, txt2, w2 = headings[i + 1]

            # 1. Mismo término inicial de contenido (ej. H1 'Agentes...' y H2 'Agentes...')
            if w1 and w2 and w1[0] == w2[0]:
                violations.append(
                    f"{file.name} → Eco entre titulares contiguos ({t1} → {t2}): ambos inician con '{w1[0]}'.\n"
                    f"   {t1}: \"{txt1}\"\n   {t2}: \"{txt2}\""
                )

            # 2. Solapamiento excesivo de palabras clave entre titulares contiguos
            if w1 and w2:
                overlap = set(w1).intersection(set(w2))
                ratio = len(overlap) / min(len(set(w1)), len(set(w2)))
                if ratio >= 0.6:
                    violations.append(
                        f"{file.name} → Solapamiento excesivo ({ratio:.0%}) entre titulares contiguos ({t1} → {t2}): "
                        f"palabras comunes: {list(overlap)}.\n"
                        f"   {t1}: \"{txt1}\"\n   {t2}: \"{txt2}\""
                    )

    assert not violations, "Ecos o redundancias entre titulares contiguos detectados:\n" + "\n".join(violations)


def test_wording_no_badge_heading_tautology():
    """Valida que no exista tautología ni eco léxico entre una pastilla (.dash-badge) y el H2 que le sigue."""
    violations = []
    badge_stop_words = SPANISH_STOP_WORDS | {
        "de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "por", "con",
        "tu", "tus", "su", "sus", "que", "te", "o", "al", "del", "no", "si", "más"
    }

    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        content_clean = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", content, flags=re.S | re.I)

        for m in re.finditer(r"<(?:div|span)\b[^>]*class=['\"][^'\"]*dash-badge[^'\"]*['\"][^>]*>(.*?)</(?:div|span)>\s*<h2\b[^>]*>(.*?)</h2>", content_clean, flags=re.S | re.I):
            badge_txt = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
            h2_txt = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
            b_words = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", badge_txt.lower()) if w not in badge_stop_words]
            h_words = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", h2_txt.lower()) if w not in badge_stop_words]

            # 1. Misma palabra inicial
            if b_words and h_words and b_words[0] == h_words[0]:
                violations.append(
                    f"{file.name} → Pastilla y H2 inician con la misma palabra '{b_words[0]}':\n"
                    f"   Badge: \"{badge_txt}\"\n   H2: \"{h2_txt}\""
                )

            # 2. Solapamiento de contenido >= 50%
            if b_words and h_words:
                overlap = set(b_words).intersection(set(h_words))
                ratio = len(overlap) / len(set(b_words))
                if ratio >= 0.5:
                    violations.append(
                        f"{file.name} → Tautología pastilla-H2 ({ratio:.0%} solapamiento): "
                        f"palabras comunes: {list(overlap)}.\n"
                        f"   Badge: \"{badge_txt}\"\n   H2: \"{h2_txt}\""
                    )

    assert not violations, "Tautologías o redundancias entre pastilla y titular detectadas:\n" + "\n".join(violations)


def test_wording_fold_anchor_diversity():
    """Valida que en el primer pliegue del Home (index.html) no se sature el vocabulario:
    H1, la primera pastilla y el primer H2 no pueden iniciar con la misma palabra clave de anclaje."""
    index_file = ROOT / "index.html"
    content = index_file.read_text(encoding="utf-8")
    content_clean = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", content, flags=re.S | re.I)

    h1_match = re.search(r"<h1\b[^>]*>(.*?)</h1>", content_clean, flags=re.S | re.I)
    badge_match = re.search(r"<(?:div|span)\b[^>]*class=['\"][^'\"]*dash-badge[^'\"]*['\"][^>]*>(.*?)</(?:div|span)>", content_clean, flags=re.S | re.I)
    h2_match = re.search(r"<h2\b[^>]*>(.*?)</h2>", content_clean, flags=re.S | re.I)

    assert h1_match and badge_match and h2_match, "Elementos clave del Hero no encontrados en index.html"

    stop_words = SPANISH_STOP_WORDS | {"de", "la", "el", "en", "y", "a", "para", "que", "tu"}

    h1_txt = re.sub(r"<[^>]+>", " ", h1_match.group(1)).strip()
    badge_txt = re.sub(r"<[^>]+>", " ", badge_match.group(1)).strip()
    h2_txt = re.sub(r"<[^>]+>", " ", h2_match.group(1)).strip()

    h1_words = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", h1_txt.lower()) if w not in stop_words]
    badge_words = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", badge_txt.lower()) if w not in stop_words]
    h2_words = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", h2_txt.lower()) if w not in stop_words]

    leading_words = [words[0] for words in [h1_words, badge_words, h2_words] if words]
    counts = collections.Counter(leading_words)
    duplicates = [word for word, count in counts.items() if count > 1]

    assert not duplicates, (
        f"Saturación de palabra ancla en el primer pliegue de index.html: palabra '{duplicates[0]}' "
        f"repetida como inicio en los elementos principales del Hero:\n"
        f"   H1: \"{h1_txt}\"\n   Badge: \"{badge_txt}\"\n   Primer H2: \"{h2_txt}\""
    )


def test_wording_section_headings_conciseness_and_density():
    """Valida que los titulares H2 de sección (.section-title) no sean ridículamente largos
    (máximo 13 palabras y 85 caracteres) ni peguen oraciones compuestas con punto seguido.
    Las buenas prácticas de UX Writing (NN/g, Julian Shapiro) exigen titulares concisos de 5 a 8 palabras
    que se escaneen en máximo 2 líneas visuales en viewport desktop y mobile."""
    violations = []
    for file in MARKETING_HTML_FILES:
        content = file.read_text(encoding="utf-8")
        for m in re.finditer(r'<h2\b[^>]*class=["\'][^"\']*section-title[^"\']*["\'][^>]*>(.*?)</h2>', content, re.I | re.S):
            h2_inner = m.group(1)
            clean_text = re.sub(r'<[^>]+>', ' ', h2_inner)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            words = clean_text.split()

            if len(words) > 13 or len(clean_text) > 85:
                violations.append(
                    f"{file.name} → H2 excesivamente largo ({len(words)} palabras, {len(clean_text)} caracteres): {clean_text!r}"
                )
            if len(words) > 13 and re.search(r'[a-záéíóúñ]{3,}\.\s+[A-ZÁÉÍÓÚÑ]', clean_text):
                violations.append(
                    f"{file.name} → H2 compuesto con dos oraciones completas unidas por punto: {clean_text!r}"
                )

    assert not violations, "Titulares H2 excesivamente largos o con oraciones compuestas detectados:\n" + "\n".join(violations)
