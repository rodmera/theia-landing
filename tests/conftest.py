"""Fixtures de la suite del sitio: servidor estático local + contextos mobile-first.

El sitio es estático (GitHub Pages). Se sirve el checkout con http.server y se
testea contra localhost — NUNCA contra theia.cl en vivo (los tests corren antes
del push; el deploy ES el push).
"""
import os
import socket
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _free_port():
    """Puerto efímero libre asignado por el SO. Evita colisiones con otros
    servicios locales (ej. el servidor A2A en :8123, que hacía que la suite
    testeara contra el server equivocado y devolviera 404 en todas las páginas)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# SITE_PORT fuerza un puerto fijo si se necesita; por defecto, uno libre por corrida.
PORT = int(os.environ["SITE_PORT"]) if os.environ.get("SITE_PORT") else _free_port()
BASE = f"http://127.0.0.1:{PORT}"

# Mobile-first: el viewport POR DEFECTO de toda la suite es un teléfono real.
MOBILE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True,
          "device_scale_factor": 3, "has_touch": True,
          "user_agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                         "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")}
DESKTOP = {"viewport": {"width": 1366, "height": 768}}

# Páginas estáticas del sitio (los _posts Jekyll requieren build de Pages — no van acá).
PAGES = ["/", "/funciones.html", "/precios.html", "/servicios.html",
         "/panel.html", "/calculadora.html", "/pulse.html",
         "/casos.html", "/nosotros.html", "/privacidad.html", "/terminos.html", "/blog/",
         "/atencion-whatsapp.html", "/cotizaciones-agendamiento.html", "/seguimiento-equipo.html",
         "/atencion-cliente.html", "/criterios.html", "/cumplimiento.html", "/crm.html", "/salud.html", "/servicios-pyme.html", "/automotriz.html", "/comercio.html", "/alternativa-crm.html", "/migracion.html"]


def _wait_port(port, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.2)
    return False


@pytest.fixture(scope="session", autouse=True)
def site_server():
    proc = subprocess.Popen(
        ["python3", str(ROOT / "tests" / "serve_local.py"), str(PORT)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert _wait_port(PORT), f"serve_local.py no levantó en :{PORT}"
    yield BASE
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="session")
def mobile_page(browser):
    """Página con viewport móvil (el default de la suite) + captura de errores JS."""
    ctx = browser.new_context(**MOBILE)
    page = ctx.new_page()
    page.js_errors = []
    page.on("pageerror", lambda e: page.js_errors.append(str(e)))
    yield page
    ctx.close()


@pytest.fixture(scope="session")
def desktop_page(browser):
    ctx = browser.new_context(**DESKTOP)
    page = ctx.new_page()
    page.js_errors = []
    page.on("pageerror", lambda e: page.js_errors.append(str(e)))
    yield page
    ctx.close()


@pytest.fixture(autouse=True)
def _reset_js_errors(request):
    """Limpia la lista de errores JS antes de cada test para no arrastrar estado en fixtures de sesión."""
    for fix in ("mobile_page", "desktop_page"):
        if fix in request.fixturenames:
            p = request.getfixturevalue(fix)
            if hasattr(p, "js_errors"):
                p.js_errors.clear()


def filtered_js_errors(page):
    """Errores JS reales: se toleran los fallos de RED del widget/analytics
    (el backend TheIA y GA no corren en el server local de tests)."""
    benign = ("Failed to fetch", "NetworkError", "net::ERR", "Load failed",
              "ERR_CONNECTION", "ERR_NAME_NOT_RESOLVED")
    return [e for e in page.js_errors if not any(b in e for b in benign)]
