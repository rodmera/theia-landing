"""Servidor HTTP local para tests que replica el comportamiento de GitHub Pages:
resuelve rutas sin extensión (.html) si el archivo correspondiente existe.
"""
import sys
import http.server
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PagesHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        translated = super().translate_path(path)
        p = Path(translated)
        if not p.exists() and not p.suffix:
            candidate = p.with_suffix(".html")
            if candidate.is_file():
                return str(candidate)
        return translated


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = http.server.HTTPServer(("127.0.0.1", port), PagesHTTPRequestHandler)
    server.serve_forever()
