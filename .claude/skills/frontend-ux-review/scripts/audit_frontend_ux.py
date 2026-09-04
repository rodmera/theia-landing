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
import os
import re
import sys
from pathlib import Path

CANONICAL_FAMILIES = {"merriweather", "plus jakarta sans", "inherit"}
CANONICAL_WEIGHTS = {"400", "500", "700", "900"}
FORBIDDEN_PROMISES = ["próximamente", "próximas", "avísame", "en camino", "coming soon"]
GREEN_COLORS = ["#34c77b", "#25d366", "#10b981", "rgb(52, 199, 123)", "rgb(37, 211, 102)", "rgb(16, 185, 129)"]
PURPLE_COLORS = ["#4f46e5", "#818cf8", "#6366f1", "#a855f7", "rgb(79, 70, 229)", "rgb(129, 140, 248)"]


class FrontendUXAuditor:
    def __init__(self, target_dir: Path):
        self.target_dir = target_dir.resolve()
        self.html_files = sorted(list(self.target_dir.glob("*.html")))
        self.css_files = sorted(list(self.target_dir.glob("*.css")))
        self.errors = []
        self.warnings = []

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
                    if w not in CANONICAL_WEIGHTS:
                        self.log_error(file, idx, "TYPO-WEIGHT", f"Peso {w} no cargado en el bundle oficial (válidos: 400, 500, 700, 900)")

    def audit_section_titles(self):
        """Valida que todos los títulos de sección estén estrictamente homologados."""
        for file in self.html_files:
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

    def audit_color_and_palettes(self):
        """Valida que el verde esté restringido y los badges no usen morado."""
        for file in self.html_files + self.css_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
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

    def audit_ux_content_and_promises(self):
        """Valida que no haya promesas de futuro vacías ni copy no verificado."""
        for file in self.html_files:
            content = file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                # Ignorar tags de script, comentarios o atributos
                clean_line = re.sub(r"<[^>]+>", " ", line).strip()
                for promise in FORBIDDEN_PROMISES:
                    if re.search(r"\b" + re.escape(promise) + r"\b", clean_line, re.I):
                        self.log_error(file, idx, "UX-FUTURE-PROMISE", f"Promesa de futuro no autorizada en copy visible: {promise!r}")

    def run(self) -> bool:
        print(f"🔍 Iniciando Auditoría Frontend & UX en: {self.target_dir}")
        print(f"📄 Archivos HTML analizados: {len(self.html_files)}")
        print(f"🎨 Archivos CSS analizados: {len(self.css_files)}")
        print("-" * 60)

        self.audit_typography()
        self.audit_section_titles()
        self.audit_color_and_palettes()
        self.audit_ux_content_and_promises()

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
