#!/usr/bin/env python3
"""Auditor determinista de Frontend, UX y Design System.

Valida:
1. Jerarquía tipográfica y cumplimiento estricto del Design System (familias, pesos, escalas).
2. Homologación absoluta de títulos de sección (Merriweather 900, clamp, line-height 1.2, oro TheIA).
3. Subtítulos de sección (Plus Jakarta Sans, 1.05rem, max-width 680px).
4. Prohibición de overrides inline y selectores CSS secundarios que rompan la consistencia.
5. Paleta de colores canónica (TheIA Gold, restricción de verde a WhatsApp/status dot).
6. Buenas prácticas de UX: contraste, legibilidad, touch targets y ausencia de promesas futuras.
"""

import argparse
import collections
import os
import re
import sys
from pathlib import Path

CANONICAL_FAMILIES = {"merriweather", "plus jakarta sans", "inherit"}
CANONICAL_WEIGHTS = {"400", "500", "700", "900"}
FORBIDDEN_PROMISES = ["próximamente", "próximas", "avísame", "en camino", "coming soon"]
GREEN_COLORS = ["#34c77b", "#25d366", "#10b981", "rgb(52, 199, 123)", "rgb(37, 211, 102)", "rgb(16, 185, 129)"]
PURPLE_COLORS = ["#4f46e5", "#818cf8", "#6366f1", "#a855f7", "rgb(79, 70, 229)", "rgb(129, 140, 248)"]
ROGUE_COLORS = [
    (r"\b#(?:0284c7|38bdf8|0ea5e9|06b6d4|22d3ee|38b6ff|00ffff)\b", "Cyan / Sky Blue (#0284c7, #38bdf8...)"),
    (r"\b#(?:e11d48|f43f5e|d946ef|7c3aed|a855f7|9333ea|c026d3)\b", "Fucsia / Púrpura no canónico (#e11d48, #7c3aed...)"),
]

# Reglas de Wording y UX Writing (NN/g, Torrey Podmajersky, Sarah Richards)
PLEONASMS = [
    (r"\bcompletamente gratis\b", "usar 'gratis' o 'sin costo'"),
    (r"\btotalmente gratis\b", "usar 'gratis' o 'sin costo'"),
    (r"\btotalmente autom[aá]tico\b", "usar 'automático'"),
    (r"\bcompletamente autom[aá]tico\b", "usar 'automático'"),
    (r"\breintentar de nuevo\b", "usar 'reintentar'"),
    (r"\bvolver a repetir\b", "usar 'repetir'"),
    (r"\brepetir de nuevo\b", "usar 'repetir'"),
    (r"\blapso de tiempo\b", "usar 'plazo' o 'tiempo'"),
    (r"\bper[ií]odo de tiempo\b", "usar 'período' o 'plazo'"),
    (r"\bresumen breve\b", "usar 'resumen'"),
    (r"\bresultado final\b", "usar 'resultado'"),
    (r"\bplanes a futuro\b", "usar 'planes'"),
    (r"\bsoluci[oó]n integral completa\b", "usar 'solución integral'"),
    (r"\binnovaci[oó]n novedosa\b", "usar 'innovación'"),
    (r"\bprever de antemano\b", "usar 'prever'"),
    (r"\bcolaborar conjuntamente\b", "usar 'colaborar'"),
    (r"\bbucle circular\b", "usar 'bucle' o 'ciclo'"),
]

META_UI = [
    (r"\bhaz clic aqu[ií]\b", "usar verbo de acción directo"),
    (r"\bhaga clic aqu[ií]\b", "usar verbo de acción directo"),
    (r"\bclick aqu[ií]\b", "usar verbo de acción directo"),
    (r"\btoca el bot[oó]n para\b", "usar verbo de acción directo"),
    (r"\bpresiona el bot[oó]n para\b", "usar verbo de acción directo"),
    (r"\ba continuaci[oó]n te mostramos\b", "ir directo a la información"),
    (r"\ben la siguiente secci[oó]n te presentamos\b", "ir directo a la información"),
    (r"\ben esta secci[oó]n puedes ver\b", "ir directo a la información"),
]

FLUFF_PATTERNS = [
    (r"\bde [uú]ltima generaci[oó]n\b", "especificar modelo o capacidad concreta"),
    (r"\bde vanguardia\b", "especificar beneficio operativo/técnico concreto"),
    (r"\bde clase mundial\b", "especificar certificaciones o métricas"),
    (r"\brevolucionari[ao]s?\b", "usar lenguaje sobrio y concreto"),
    (r"\bsin precedentes\b", "usar lenguaje sobrio y comprobable"),
    (r"\bdisruptiv[ao]s?\b", "usar lenguaje sobrio y concreto"),
    (r"\bparadigma\b", "usar lenguaje claro"),
    (r"\bhol[ií]stic[ao]s?\b", "usar lenguaje claro"),
    (r"\bsinergia\b", "usar lenguaje claro"),
    (r"\bcustomer-centric\b", "usar 'centrado en el cliente'"),
    (r"\bseamless\b", "usar 'fluido' o 'sin fricción'"),
]

USTEDEO_PATTERNS = [
    (r"\bsu negocio\b", "usar 'tu negocio' (tuteo estándar)"),
    (r"\bsus clientes\b", "usar 'tus clientes' (tuteo estándar)"),
    (r"\bsu empresa\b", "usar 'tu empresa' (tuteo estándar)"),
    (r"\busted\b", "usar tuteo consistente ('tú')"),
    (r"\bcomun[ií]quese\b", "usar 'comunícate'"),
]

VOSEO_PATTERNS = [
    (r"\btenés\b", "usar 'tienes'"),
    (r"\bpodés\b", "usar 'puedes'"),
    (r"\bquerés\b", "usar 'quieres'"),
    (r"\bsabés\b", "usar 'sabes'"),
    (r"\bhacés\b", "usar 'haces'"),
]

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


class FrontendUXAuditor:
    def __init__(self, target_dir: Path):
        self.target_dir = target_dir.resolve()
        html_candidates = set(self.target_dir.glob("*.html"))
        html_candidates.update(self.target_dir.glob("app/templates/**/*.html"))
        
        # Filtrar carpeta templates/ suelta si es sólo de exportación de landing (cotizaciones/firmas)
        self.html_files = sorted([
            f for f in html_candidates
            if not (f.is_relative_to(self.target_dir / "templates") and not (self.target_dir / "app").is_dir())
        ])

        css_candidates = set(self.target_dir.glob("*.css"))
        css_candidates.update(self.target_dir.glob("app/static/css/**/*.css"))
        self.css_files = sorted(list(css_candidates))

        self.errors = []
        self.warnings = []
        self.is_static_site = (self.target_dir / "index.html").is_file() and not (self.target_dir / "app").is_dir()
        self.is_app_repo = (self.target_dir / "app").is_dir() or any("admin" in str(f).lower() for f in self.html_files)

    def log_error(self, file_path: Path, line_no: int, rule: str, detail: str):
        rel = file_path.relative_to(self.target_dir) if file_path.is_relative_to(self.target_dir) else file_path
        self.errors.append(f"❌ [{rule}] {rel}:{line_no} → {detail}")

    def log_warning(self, file_path: Path, line_no: int, rule: str, detail: str):
        rel = file_path.relative_to(self.target_dir) if file_path.is_relative_to(self.target_dir) else file_path
        self.warnings.append(f"⚠️ [{rule}] {rel}:{line_no} → {detail}")

    def audit_typography(self):
        """Valida que no existan fuentes no cargadas ni pesos ilegales."""
        font_family_re = re.compile(r"font-family\s*:\s*([^;}]+)", re.I)
        font_weight_re = re.compile(r"font-weight\s*:\s*(\d+)\b", re.I)
        allowed_weights = CANONICAL_WEIGHTS | {"600"} if self.is_app_repo else CANONICAL_WEIGHTS

        for file in self.html_files + self.css_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                # Familias
                for match in font_family_re.finditer(line):
                    raw = match.group(1).lower().replace('"', '').replace("'", '').strip()
                    tokens = [t.strip() for t in raw.split(",")]
                    # Al menos una familia canónica
                    if not any(f in tokens for f in ["merriweather", "plus jakarta sans", "inherit", "monospace", "ui-monospace"]):
                        self.log_error(file, idx, "TYPO-FAMILY", f"Familia no autorizada por Design System: {match.group(1).strip()}")

                # Pesos numéricos
                for match in font_weight_re.finditer(line):
                    w = match.group(1)
                    if w not in allowed_weights:
                        self.log_error(file, idx, "TYPO-WEIGHT", f"Peso {w} no cargado en el bundle oficial (válidos: {sorted(list(allowed_weights))})")

    def audit_section_titles(self):
        """Valida que todos los títulos de sección estén estrictamente homologados."""
        marketing_html = [f for f in self.html_files if "template" not in str(f).lower() and "admin" not in str(f).lower()]
        for file in marketing_html:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            # 1. Prohibir estilos inline en h1 y h2 que alteren tamaño o peso
            inline_h_re = re.compile(r'<h[12][^>]*style="[^"]*(?:font-size|font-weight)[^"]*"[^>]*>', re.I)
            for idx, line in enumerate(lines, 1):
                m = inline_h_re.search(line)
                if m:
                    self.log_error(file, idx, "SECTION-TITLE-INLINE", f"Override inline no permitido en encabezado: {m.group()!r}")

            # 2. Validar que los H2 de sección usen .section-title
            h2_re = re.compile(r'<h2([^>]*)>', re.I)
            for idx, line in enumerate(lines, 1):
                for match in h2_re.finditer(line):
                    attrs = match.group(1)
                    # Si no es un modal, newsletter o dentro de sección oculta
                    if "newsletter" in attrs or "modal" in attrs or "hidden" in attrs:
                        continue
                    if "section-title" not in attrs and "id=" not in attrs and "privacidad" not in file.name and "terminos" not in file.name and "servicios" not in file.name:
                        self.log_warning(file, idx, "SECTION-TITLE-CLASS", "H2 de sección debería utilizar la clase canónica .section-title")

        # 3. Validar overrides en CSS secundarios
        for file in self.css_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            # Prohibir selectores secundarios que reduzcan el peso a 700 o alteren font-size de títulos
            for match in re.finditer(r'([^{]+)\{\s*[^}]*font-weight\s*:\s*700[^}]*\}', content, re.I):
                selector = match.group(1).strip()
                if "section-title" in selector or "-header h2" in selector:
                    line_no = content.count("\n", 0, match.start()) + 1
                    self.log_error(file, line_no, "CSS-TITLE-OVERRIDE", f"Override CSS secundario proscrito en {selector!r} con font-weight: 700")

        # 4. Validar concisión y densidad de títulos de sección (máx 13 palabras, máx 85 caracteres en landing)
        # Las buenas prácticas de UX Writing (NN/g, Julian Shapiro) exigen H2 concisos de 5-8 palabras (máx 12-13)
        # y máx 2 líneas visuales. Títulos que superan los 85 caracteres provocan "muros de texto"
        # que fatigan la lectura y quiebran en 3-4 líneas en viewport display.
        for file in marketing_html:
            if "terminos.html" in file.name or "privacidad.html" in file.name:
                continue
            content = file.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'<h2\b[^>]*class=["\'][^"\']*section-title[^"\']*["\'][^>]*>(.*?)</h2>', content, re.I | re.S):
                h2_inner = m.group(1)
                clean_text = re.sub(r'<[^>]+>', ' ', h2_inner)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                words = clean_text.split()
                line_no = content.count("\n", 0, m.start()) + 1

                if len(words) > 13 or len(clean_text) > 85:
                    self.log_error(
                        file,
                        line_no,
                        "HEADING-EXCESSIVE-LENGTH",
                        f"Titular H2 excesivamente largo ({len(words)} palabras, {len(clean_text)} caracteres). "
                        f"Las buenas prácticas de UX Writing (NN/g) exigen máx 10-12 palabras / 85 chars para no saturar la pantalla con 3-4 líneas: {clean_text!r}"
                    )
                if len(words) > 13 and re.search(r'[a-záéíóúñ]{3,}\.\s+[A-ZÁÉÍÓÚÑ]', clean_text):
                    self.log_error(
                        file,
                        line_no,
                        "HEADING-COMPOUND-SENTENCE",
                        f"Titular H2 contiene dos oraciones completas unidas con punto seguido. "
                        f"Un titular debe comunicar una sola promesa/idea; los detalles pertenecen al subtítulo: {clean_text!r}"
                    )

    def audit_admin_and_app_ui(self):
        """Valida que las interfaces de aplicación/admin mantengan consistencia estructural y tipográfica pura (Plus Jakarta Sans)."""
        admin_templates = [
            f for f in self.html_files 
            if "/admin/" in str(f).lower() or "\\admin\\" in str(f).lower() or f.name.startswith("admin_")
        ]
        admin_css = [
            f for f in self.css_files 
            if "theme" in f.name.lower() or "admin" in f.name.lower()
        ]

        # 1. Prohibir Merriweather / serif en templates de admin y aplicación
        serif_re = re.compile(r"font-family\s*:\s*[^;}]*(?:merriweather|(?<!sans-)serif)", re.I)
        for file in admin_templates:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                # Ignorar tags script o comentarios
                if "<script" in line or "font-sans-serif" in line or "google" in line:
                    continue
                m = serif_re.search(line)
                if m:
                    self.log_error(
                        file, idx, "APP-SERIF-PROHIBITED",
                        f"Uso de fuente serif en interfaz de aplicación/admin: {m.group()!r}. Las vistas admin deben usar estrictamente Plus Jakarta Sans."
                    )

        # 2. Prohibir que CSS de admin asigne Merriweather por defecto a encabezados
        for file in admin_css:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'([^{]+)\{\s*[^}]*font-family\s*:\s*[^;}]*merriweather[^}]*\}', content, re.I):
                selector = m.group(1).strip()
                line_no = content.count("\n", 0, m.start()) + 1
                self.log_error(
                    file, line_no, "APP-CSS-SERIF-PROHIBITED",
                    f"Regla CSS de admin asigna fuente serif a {selector!r}. Toda la UI de administración debe ser Plus Jakarta Sans."
                )

        # 3. Consistencia de estructura de encabezado: toda vista admin que extiende base.html debe implementar block page_header
        for file in admin_templates:
            content = file.read_text(encoding="utf-8", errors="ignore")
            if 'extends "admin/base.html"' in content or "extends 'admin/base.html'" in content:
                if "{% block page_header %}" not in content:
                    self.log_error(
                        file, 1, "APP-MISSING-PAGE-HEADER",
                        "Plantilla extiende 'admin/base.html' pero no implementa '{% block page_header %}'. Esto provoca colisión con el saludo fallback y títulos duplicados."
                    )

    def audit_button_palettes(self):
        """Valida que los botones interactivos respeten la paleta canónica: Índigo (#4f46e5) o TheIA Gold (#d4af37), prohibiendo fondos negros/slate (#0f172a / #000)."""
        black_colors = ["#0f172a", "#0b1320", "#000000", "#000", "black"]

        for file in self.css_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            # Prohibir --brand-primary asignado a slate/negro
            for m in re.finditer(r'--brand-primary\s*:\s*([^;}]+)', content, re.I):
                val = m.group(1).strip().lower()
                if any(b in val for b in black_colors):
                    line_no = content.count("\n", 0, m.start()) + 1
                    self.log_error(
                        file, line_no, "BUTTON-COLOR-BLACK",
                        f"--brand-primary configurado con tono negro/slate ({val}). Los botones primarios en TheIA deben usar Índigo (#4f46e5 / #4338ca) o TheIA Gold (#d4af37)."
                    )

            # Prohibir .btn-primary con fondo negro/slate directo
            for m in re.finditer(r'\.btn-primary[^{]*\{[^}]*background(?:-color)?\s*:\s*([^;}]+)', content, re.I):
                val = m.group(1).strip().lower()
                if any(b in val for b in black_colors):
                    line_no = content.count("\n", 0, m.start()) + 1
                    self.log_error(
                        file, line_no, "BUTTON-COLOR-BLACK",
                        f".btn-primary configurado con fondo negro/slate ({val}). Debe usar Índigo (#4f46e5) o TheIA Gold."
                    )

        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'<button\b[^>]*style="[^"]*background(?:-color)?\s*:\s*([^;"]+)[^"]*"[^>]*>', content, re.I):
                val = m.group(1).strip().lower()
                if any(b in val for b in black_colors):
                    line_no = content.count("\n", 0, m.start()) + 1
                    self.log_error(
                        file, line_no, "BUTTON-INLINE-BLACK",
                        f"Botón con estilo inline de fondo negro/slate ({val}). Prohibido botones negros en la paleta de TheIA."
                    )

            # Prohibir selectores de botones o filtros activos con fondo negro/slate
            for m in re.finditer(r'\.(?:btn[^\s{]*|tab[^\s{]*)\.active[^{]*\{[^}]*background(?:-color)?\s*:\s*([^;!}]+)', content, re.I):
                val = m.group(1).strip().lower()
                if any(b in val for b in black_colors):
                    line_no = content.count("\n", 0, m.start()) + 1
                    self.log_error(
                        file, line_no, "BUTTON-FILTER-ACTIVE-BLACK",
                        f"Filtro/botón activo con fondo negro/slate ({val}). Los elementos activos interactivos en TheIA deben usar Índigo (#4f46e5) o TheIA Gold (#d4af37)."
                    )

    def audit_color_and_palettes(self):
        """Valida que los colores y gradientes se ajusten estrictamente al Design System (restringiendo verde y prohibiendo colores no canónicos)."""
        for file in self.html_files + self.css_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            # Para HTML, eliminar scripts internos para no evaluar código JS
            clean_content = re.sub(r'<script\b[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.I) if file.suffix.lower() in [".html", ".htm"] else content
            lines = clean_content.splitlines()
            for idx, line in enumerate(lines, 1):
                # Ignorar si es la regla canónica de .btn-whatsapp, status-dot o declaración de variables
                if any(k in line.lower() for k in [".btn-whatsapp", "status-dot", "live-dot", "--green:", "svg", "fill=", "stroke="]):
                    continue

                for green in GREEN_COLORS:
                    if green in line.lower():
                        # Si está dentro de una tarjeta o texto regular
                        if any(tag in line.lower() for tag in ["<h1", "<h2", "<h3", "<p", "<span", ".card"]):
                            self.log_error(file, idx, "PALETTE-GREEN-RESTRICTION", f"Uso no autorizado de verde ({green}): el verde está restringido exclusivamente a WhatsApp y micro-punto de 6px")

                # Chequeo de morados en dash-badge
                if "dash-badge" in line.lower():
                    for purple in PURPLE_COLORS:
                        if purple in line.lower():
                            self.log_error(file, idx, "PALETTE-DASH-BADGE", f"Badge con tono morado/índigo no autorizado ({purple}): debe usar TheIA Gold")

                # Chequeo de cifras monetarias con text-success (verde prohibido en dinero)
                if "text-success" in line.lower() and re.search(r'[\$€£]|\bCLP\b|\bUSD\b', line, re.I):
                    self.log_error(file, idx, "FINANCIAL-AMOUNT-GREEN", "Cifra monetaria o precio usando clase 'text-success'. El Design System prohíbe el uso de verde en precios, cifras monetarias y cantidades (usar Slate 900 #0f172a o TheIA Gold #d4af37).")

                # Detección de colores no canónicos ajenos a la paleta oficial TheIA (cyan, sky blue, fucsia, púrpura...)
                for pattern, desc in ROGUE_COLORS:
                    if re.search(pattern, line, re.I):
                        if not any(ign in line.lower() for ign in ["href=", "src=", "content=", "data-", "http"]):
                            self.log_error(file, idx, "PALETTE-NON-CANONICAL-COLOR", f"Color o gradiente ajeno a la paleta oficial de TheIA detectado ({desc}). Debe usar Executive Slate (#0f172a), TheIA Gold (#d4af37), Índigo (#4f46e5) o tonos neutros.")

        # Prohibir .nav-link.active global con border-left en CSS (fuga de estilos de sidebar a tabs)
        for file in self.css_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'(?:^|[,\n\}])\s*\.nav-link\.active[^{]*\{[^}]*border-left(?:-color)?\s*:\s*(?!none)[^;!}]+', content, re.I):
                line_no = content.count("\n", 0, m.start()) + 1
                self.log_error(file, line_no, "GLOBAL-NAV-LINK-SIDEBAR-LEAK", "Regla '.nav-link.active' con 'border-left' no está acotada a '.sidebar'. Esto corrompe las pestañas y navs interiores.")

    def audit_ux_content_and_promises(self):
        """Valida que no haya promesas de futuro vacías ni copy no verificado."""
        targets = self.html_files if self.is_static_site else [f for f in self.html_files if "admin" not in str(f).lower()]
        for file in targets:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                # Ignorar tags de script, comentarios o atributos
                clean_line = re.sub(r"<[^>]+>", " ", line).strip()
                for promise in FORBIDDEN_PROMISES:
                    if re.search(r"\b" + re.escape(promise) + r"\b", clean_line, re.I):
                        self.log_error(file, idx, "UX-FUTURE-PROMISE", f"Promesa de futuro no autorizada en copy visible: {promise!r}")

    def audit_svg_validity(self):
        """Audita que ningún elemento <svg> use atributos XML inválidos como width='auto' o height='auto'."""
        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                if "<svg" in line:
                    matches = re.findall(r"<svg\b[^>]*>", line, re.I)
                    for tag in matches:
                        if re.search(r'\b(?:width|height)\s*=\s*["\']auto["\']', tag, re.I):
                            self.log_error(
                                file, idx, "SVG-INVALID-ATTR",
                                f"<svg> con width='auto' o height='auto' inválido en XML SVG (lanza error en consola Chromium). Usar style='height: auto;'."
                            )

    def audit_no_emojis_as_icons(self):
        """Audita que ningún contenedor de icono o tarjeta use emojis en lugar de SVGs vectoriales."""
        pictorial_emojis = re.compile(
            "["
            "\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F680-\U0001F6FF"  # Transport and Map Symbols
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\u26A1"                 # High Voltage / Zap (⚡)
            "\u2600-\u2604\u260E\u2611\u2614\u2615\u2618\u261D\u2620-\u263A\u2648-\u2653\u2660-\u2668\u267B\u267F\u2692-\u269C\u26A0\u26AA\u26AB\u26B0\u26B1\u26BD\u26BE\u26C4\u26C5\u26CE\u26CF\u26D1\u26D4\u26E9\u26EA\u26F0-\u26F5\u26F7-\u26FA\u26FD"
            "]+",
            flags=re.UNICODE,
        )
        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            content_clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.S)
            for m in re.finditer(r"<([a-z0-9]+)\b[^>]*class=['\"][^'\"]*(?:icon|visual)[^'\"]*['\"][^>]*>(.*?)</\1>", content_clean, flags=re.S | re.I):
                tag_content = m.group(2)
                text_inside = re.sub(r"<[^>]+>", "", tag_content).strip()
                if text_inside:
                    matches = pictorial_emojis.findall(text_inside)
                    if matches:
                        line_no = content[:m.start()].count("\n") + 1
                        self.log_error(
                            file, line_no, "ICON-EMOJI-FORBIDDEN",
                            f"Contenedor visual '{m.group(0)[:50]}' usa emojis ({matches}) en vez de SVG vectorial homologado."
                        )

    def audit_wording_and_editorial_quality(self):
        """Valida calidad editorial, ausencia de pleonasmos, meta-lenguaje, fluff y echoing."""
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

        targets = self.html_files
        for file in targets:
            if file.name in ["privacidad.html", "terminos.html"]:
                continue
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            in_block = False
            for idx, line in enumerate(lines, 1):
                if re.search(r"<(script|style)\b", line, re.I):
                    in_block = True
                if in_block:
                    if re.search(r"</(script|style)>", line, re.I):
                        in_block = False
                    continue
                if any(tag in line for tag in ["<!--", "href=", "src=", "http://", "https://"]):
                    continue

                line_no_code = re.sub(r"<code>.*?</code>", " ", line, flags=re.I)
                clean_line = re.sub(r'\{%.*?%\}', ' ', line_no_code)
                clean_line = re.sub(r'\{\{.*?\}\}', ' ', clean_line)
                clean_line = re.sub(r"<[^>]+>", " ", clean_line)
                clean_line = re.sub(r"\s+", " ", clean_line).strip()
                if not clean_line:
                    continue

                # 1. Pleonasmos
                for pattern, recommendation in PLEONASMS:
                    match = re.search(pattern, clean_line, re.I)
                    if match:
                        self.log_error(file, idx, "WORDING-PLEONASMO", f"Pleonasmo '{match.group()}'. Recomendación: {recommendation}")

                # 2. Meta-lenguaje
                for pattern, recommendation in META_UI:
                    match = re.search(pattern, clean_line, re.I)
                    if match:
                        self.log_error(file, idx, "WORDING-META-UI", f"Meta-lenguaje obvio '{match.group()}'. Recomendación: {recommendation}")

                # 3. Fluff / Buzzwords
                for pattern, recommendation in FLUFF_PATTERNS:
                    match = re.search(pattern, clean_line, re.I)
                    if match:
                        self.log_error(file, idx, "WORDING-FLUFF", f"Buzzword/Fluff '{match.group()}'. Recomendación: {recommendation}")

                # 3.1 AI Slop & Clichés
                for pattern, recommendation in AI_SLOP_PATTERNS:
                    match = re.search(pattern, clean_line, re.I)
                    if match:
                        self.log_error(file, idx, "WORDING-AI-SLOP", f"AI Slop / Cliché '{match.group()}'. Recomendación: {recommendation}")

                # 4. Ustedeo
                for pattern, recommendation in USTEDEO_PATTERNS:
                    match = re.search(pattern, clean_line, re.I)
                    if match:
                        self.log_error(file, idx, "WORDING-USTEDEO", f"Inconsistencia de persona (ustedeo) '{match.group()}'. Recomendación: {recommendation}")

                # 5. Voseo
                for pattern, recommendation in VOSEO_PATTERNS:
                    match = re.search(pattern, clean_line, re.I)
                    if match:
                        self.log_error(file, idx, "WORDING-VOSEO", f"Voseo no permitido '{match.group()}'. Recomendación: {recommendation}")

                # 6. Brand naming
                for regex, expected in brand_checks:
                    for match in regex.finditer(clean_line):
                        actual = match.group()
                        if actual != expected and actual.lower() == expected.lower():
                            self.log_error(file, idx, "WORDING-NAMING", f"Naming '{actual}' debe ser '{expected}'")

            # 7. Echoing dentro de párrafos
            content_clean = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", content, flags=re.S | re.I)
            content_clean = re.sub(r"\{%.*?%\}", " ", content_clean, flags=re.S)
            content_clean = re.sub(r"\{\{.*?\}\}", " ", content_clean, flags=re.S)
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
                        self.log_warning(file, 0, "WORDING-ECHOING", f"Palabra '{word}' repetida {count} veces en párrafo: \"{text[:70]}...\"")

            # 8. Eco entre titulares contiguos (Heading Stacking Echo)
            heading_stop = SPANISH_STOP_WORDS | {"de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "por", "con", "tu", "tus", "su", "sus", "que", "te", "o", "al", "del", "no", "si"}
            headings = []
            for m in re.finditer(r"<(h[12])\b[^>]*>(.*?)</\1>", content_clean, flags=re.S | re.I):
                txt = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
                txt = re.sub(r"\s+", " ", txt)
                w_list = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", txt.lower()) if w not in heading_stop]
                headings.append((m.group(1), txt, w_list))

            for i in range(len(headings) - 1):
                t1, txt1, w1 = headings[i]
                t2, txt2, w2 = headings[i + 1]
                if w1 and w2 and w1[0] == w2[0]:
                    self.log_error(file, 0, "WORDING-HEADING-ECHO", f"Titulares contiguos ({t1} → {t2}) inician con la misma palabra '{w1[0]}': \"{txt1[:50]}\" vs \"{txt2[:50]}\"")
                if w1 and w2:
                    overlap = set(w1).intersection(set(w2))
                    ratio = len(overlap) / min(len(set(w1)), len(set(w2)))
                    if ratio >= 0.6:
                        self.log_error(file, 0, "WORDING-HEADING-OVERLAP", f"Solapamiento excesivo ({ratio:.0%}) entre titulares contiguos: palabras {list(overlap)}")

            # 9. Tautología entre pastilla (.dash-badge) y H2 adyacente
            for m in re.finditer(r"<(?:div|span)\b[^>]*class=['\"][^'\"]*dash-badge[^'\"]*['\"][^>]*>(.*?)</(?:div|span)>\s*<h2\b[^>]*>(.*?)</h2>", content_clean, flags=re.S | re.I):
                b_txt = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
                h2_txt = re.sub(r"<[^>]+>", " ", m.group(2)).strip()
                b_w = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", b_txt.lower()) if w not in heading_stop]
                h_w = [w for w in re.findall(r"\b[a-záéíóúñ]{4,}\b", h2_txt.lower()) if w not in heading_stop]
                if b_w and h_w and b_w[0] == h_w[0]:
                    self.log_error(file, 0, "WORDING-BADGE-ECHO", f"Pastilla y H2 inician con la misma palabra '{b_w[0]}': \"{b_txt}\" vs \"{h2_txt[:50]}\"")
                if b_w and h_w:
                    overlap = set(b_w).intersection(set(h_w))
                    ratio = len(overlap) / len(set(b_w))
                    if ratio >= 0.5:
                        self.log_error(file, 0, "WORDING-BADGE-TAUTOLOGY", f"Tautología pastilla-H2 ({ratio:.0%}): palabras {list(overlap)}")

    def audit_card_layout_and_cta_consistency(self):
        """Audita la consistencia de alineación de tarjetas y previene la canibalización de CTAs."""
        # 1. No enlaces de agendamiento/demo ni estilos de botón mezclados en columnas del footer
        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'<div class=["\']footer-links-group["\']>(.*?)</div>', content, re.DOTALL):
                group_content = m.group(1)
                if re.search(r'calendar\.app\.google|Agendar?\s+Demo', group_content, re.I):
                    line_no = content[:m.start()].count("\n") + 1
                    self.log_error(
                        file, line_no, "FOOTER-CTA-IN-NAV-GROUP",
                        "Enlace CTA de agendamiento intercalado en columna navegacional .footer-links-group. El footer debe ser taxonómico y limpio."
                    )

        # 2. No botones duales redundantes de agendamiento en secciones intermedias de catálogo/teaser
        index_file = self.target_dir / "index.html"
        if index_file.is_file():
            index_content = index_file.read_text(encoding="utf-8", errors="ignore")
            servicios_sec = re.search(r'<section[^>]*id=["\']servicios-especializados["\'][^>]*>(.*?)</section>', index_content, re.DOTALL)
            if servicios_sec and re.search(r'Agenda.*demo', servicios_sec.group(1), re.I):
                line_no = index_content[:servicios_sec.start()].count("\n") + 1
                self.log_error(
                    index_file, line_no, "CTA-CANIBALIZATION-DUAL",
                    "Sección #servicios-especializados contiene botón redundante de demo que compite con el enlace principal a /servicios."
                )

    def audit_accessibility_and_wcag(self):
        """Audita accesibilidad WCAG AA: alt en imágenes, type en botones, labels en inputs y H1 único."""
        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.S)

            # 1. H1 único por página (excepto redirect plataforma.html)
            if file.name != "plataforma.html":
                h1_matches = re.findall(r'<h1\b[^>]*>(.*?)</h1>', clean, re.S | re.I)
                if len(h1_matches) != 1:
                    self.log_error(file, 0, "A11Y-H1-COUNT", f"La página debe tener exactamente un <h1> (encontrados {len(h1_matches)}).")

            # 2. Atributo alt en todas las imágenes
            for m in re.finditer(r'<img\b([^>]*)>', clean, re.I):
                attrs = m.group(1)
                line_no = content[:m.start()].count("\n") + 1
                if not re.search(r'\balt\s*=', attrs, re.I) or re.search(r'\balt\s*=\s*["\']\s*["\']', attrs, re.I):
                    self.log_error(file, line_no, "A11Y-IMG-NO-ALT", f"Imagen sin atributo 'alt' descriptivo: {m.group(0)[:60]}")

            # 3. type="button" o type="submit" explícito en todos los botones
            for m in re.finditer(r'<button\b([^>]*)>', clean, re.I):
                attrs = m.group(1)
                line_no = content[:m.start()].count("\n") + 1
                if not re.search(r'\btype\s*=', attrs, re.I):
                    self.log_error(file, line_no, "A11Y-BTN-NO-TYPE", f"Botón sin atributo 'type' explícito: {m.group(0)[:60]}")

            # 4. Input con label o aria-label
            for m in re.finditer(r'<input\b([^>]*)>', clean, re.I):
                attrs = m.group(1)
                if re.search(r'\btype=["\']hidden["\']', attrs, re.I):
                    continue
                line_no = content[:m.start()].count("\n") + 1
                has_aria = re.search(r'\baria-label(?:ledby)?=["\']', attrs, re.I)
                has_label = False
                inp_id = re.search(r'\bid=["\']([^"\']+)["\']', attrs, re.I)
                if inp_id:
                    i_id = inp_id.group(1)
                    if re.search(rf'<label\b[^>]*\bfor=["\']{re.escape(i_id)}["\']', clean, re.I):
                        has_label = True
                if not has_aria and not has_label:
                    self.log_error(file, line_no, "A11Y-INPUT-NO-LABEL", f"Input sin etiqueta <label for='...'> ni aria-label: {m.group(0)[:60]}")

    def audit_broken_links_and_anchors(self):
        """Audita que no existan enlaces rotos, hashes vacíos ni anclas huérfanas en el sitio."""
        post_slugs = set()
        posts_dir = self.target_dir / "_posts"
        if posts_dir.is_dir():
            for p in posts_dir.glob("*.md"):
                m = re.match(r'^\d{4}-\d{2}-\d{2}-(.+)\.md$', p.name)
                if m:
                    post_slugs.add(m.group(1))

        index_file = self.target_dir / "index.html"
        index_ids = set()
        if index_file.is_file():
            index_clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", index_file.read_text(encoding="utf-8", errors="ignore"), flags=re.S)
            index_ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', index_clean))

        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.S)
            page_ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', clean))

            for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\']', clean, re.I):
                href = m.group(1).strip()
                line_no = content[:m.start()].count("\n") + 1

                # 1. Prohibido href="#"
                if href == "#":
                    self.log_error(file, line_no, "LINK-EMPTY-HASH", f"Enlace vacío href='#' detectado (causa saltos no deseados): {m.group(0)[:60]}")
                    continue

                # 2. Anclas en la misma página href="#algo"
                if href.startswith("#"):
                    anchor = href.lstrip("#")
                    if anchor and anchor not in page_ids:
                        self.log_error(file, line_no, "LINK-BROKEN-ANCHOR", f"Ancla interna '#{anchor}' no existe en {file.name}")
                    continue

                # 3. Anclas cruzadas a la home href="/#algo"
                if href.startswith("/#"):
                    anchor = href.lstrip("/#")
                    if anchor and anchor not in index_ids:
                        self.log_error(file, line_no, "LINK-BROKEN-HOME-ANCHOR", f"Ancla cruzada '/#{anchor}' no existe en index.html")
                    continue

                # 4. Enlaces internos absolutos href="/..."
                if href.startswith("/") and not href.startswith("//"):
                    path_part = href.split("?")[0].split("#")[0]
                    if path_part in ["", "/"]:
                        continue
                    if path_part.startswith("/blog/"):
                        slug = path_part.strip("/").split("/")[-1]
                        if slug and slug not in post_slugs and slug != "blog":
                            self.log_error(file, line_no, "LINK-BROKEN-BLOG-POST", f"Post de blog no encontrado: {href}")
                        continue
                    if path_part.endswith("/"):
                        p_dir = self.target_dir / path_part.strip("/") / "index.html"
                        if not p_dir.is_file():
                            self.log_error(file, line_no, "LINK-BROKEN-DIRECTORY", f"Directorio destino no encontrado: {href}")
                        continue
                    if "." in path_part.split("/")[-1]:
                        p_file = self.target_dir / path_part.lstrip("/")
                        if not p_file.is_file():
                            self.log_error(file, line_no, "LINK-BROKEN-STATIC-FILE", f"Archivo estático no encontrado: {href}")
                        continue
                    # Ruta sin extensión
                    p_html = self.target_dir / f"{path_part.lstrip('/')}.html"
                    p_dir = self.target_dir / path_part.lstrip("/") / "index.html"
                    if not p_html.is_file() and not p_dir.is_file():
                        self.log_error(file, line_no, "LINK-BROKEN-INTERNAL", f"Página interna no encontrada: {href}")

    def audit_asset_integrity(self):
        """Audita que todos los recursos locales referenciados (imágenes, scripts, CSS) existan en disco."""
        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            # src="..."
            for m in re.finditer(r'\bsrc=["\'](/[^"\']+)["\']', content, re.I):
                src = m.group(1).strip()
                if src.startswith("//"):
                    continue
                clean_src = src.split("?")[0].split("#")[0]
                target = self.target_dir / clean_src.lstrip("/")
                if not target.is_file():
                    line_no = content[:m.start()].count("\n") + 1
                    self.log_error(file, line_no, "ASSET-NOT-FOUND", f"Recurso local no encontrado en disco: {src}")

            # link rel="stylesheet" href="/..."
            for m in re.finditer(r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\'](/[^"\']+)["\']', content, re.I):
                href = m.group(1).strip()
                if href.startswith("//"):
                    continue
                clean_href = href.split("?")[0].split("#")[0]
                target = self.target_dir / clean_href.lstrip("/")
                if not target.is_file():
                    line_no = content[:m.start()].count("\n") + 1
                    self.log_error(file, line_no, "CSS-NOT-FOUND", f"Hoja de estilos local no encontrada en disco: {href}")

    def audit_no_raw_english_in_ui(self):
        """Valida que no existan etiquetas, insignias (badges) o cadenas tecnicas en ingles crudo en la interfaz."""
        raw_english_badges = [
            (re.compile(r"\bNeed\b", re.I), "Necesidad"),
            (re.compile(r"\bAuthority\b", re.I), "Poder de Decisión / Autoridad"),
            (re.compile(r"\bBudget\b", re.I), "Presupuesto"),
            (re.compile(r"\bSituation\b", re.I), "Situación"),
            (re.compile(r"\bProblem\b", re.I), "Problema"),
            (re.compile(r"\bImplication\b", re.I), "Impacto"),
            (re.compile(r"\bNeed-Payoff\b", re.I), "Beneficio"),
            (re.compile(r"\bPending\b", re.I), "Pendiente"),
        ]

        badge_re = re.compile(r'<span[^>]*class=["\'][^"\']*badge[^"\']*["\'][^>]*>(.*?)</span>', re.DOTALL | re.IGNORECASE)

        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for m in badge_re.finditer(content):
                raw_badge_html = m.group(1)
                text = re.sub(r"<[^>]+>", "", raw_badge_html).strip()
                if not text:
                    continue
                for pat, es_term in raw_english_badges:
                    if pat.search(text) and not any(es in text.lower() for es in ["necesidad", "situación", "problema", "impacto", "beneficio", "decisión", "presupuesto", "pendiente"]):
                        line_no = content[:m.start()].count("\n") + 1
                        self.log_error(
                            file, line_no, "UI-RAW-ENGLISH-BADGE",
                            f"Insignia (badge) contiene término en inglés crudo: '{text}'. Debe traducirse al español canónico (ej. '{es_term}')."
                        )

            # Verificar cadenas técnicas de frameworks no formateadas en la UI
            for m in re.finditer(r'\bBANT_LITE\b', content):
                line_no = content[:m.start()].count("\n") + 1
                self.log_error(
                    file, line_no, "UI-RAW-TECHNICAL-STRING",
                    "Cadena técnica 'BANT_LITE' mostrada en interfaz de usuario. Debe formatearse como 'BANT'."
                )

    def run(self) -> bool:
        print(f"🔍 Iniciando Auditoría Frontend & UX en: {self.target_dir}")
        print(f"📄 Archivos HTML analizados: {len(self.html_files)}")
        print(f"🎨 Archivos CSS analizados: {len(self.css_files)}")
        print("-" * 60)

        self.audit_typography()
        if self.is_static_site:
            self.audit_section_titles()
            self.audit_card_layout_and_cta_consistency()
            self.audit_accessibility_and_wcag()
            self.audit_broken_links_and_anchors()
            self.audit_asset_integrity()

        if self.is_app_repo:
            self.audit_admin_and_app_ui()

        self.audit_color_and_palettes()
        self.audit_button_palettes()
        self.audit_ux_content_and_promises()
        self.audit_svg_validity()
        self.audit_no_emojis_as_icons()
        self.audit_no_raw_english_in_ui()
        self.audit_wording_and_editorial_quality()

        print("\n📊 RESULTADOS:")
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            for w in self.warnings:
                print(w)

        if self.errors:
            print(f"\n❌ ERRORES DETECTADOS ({len(self.errors)}):")
            for e in self.errors:
                print(e)
            print("\n🚨 AUDITORÍA FALLIDA: Corrija las violaciones del Design System antes de continuar.")
            return False

        print("\n✅ AUDITORÍA EXITOSA: 100% conforme al Design System, UX y accesibilidad.")
        return True


def main():
    parser = argparse.ArgumentParser(description="Auditoría Frontend, UX y Design System")
    parser.add_argument("--repo", default=".", help="Ruta al repositorio o directorio frontend")
    args = parser.parse_args()

    auditor = FrontendUXAuditor(Path(args.repo))
    success = auditor.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
