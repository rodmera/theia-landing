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

# Mobile-first: el viewport POR DEFECTO de toda la suite es un teléfono real (390x844 CSS px).
# device_scale_factor=1 evita renderizar 9x más píxeles en software rasterizer (--disable-gpu),
# reduciendo full_page screenshots de ~13s a ~0.24s por página sin alterar el layout CSS.
MOBILE = {"viewport": {"width": 390, "height": 844}, "is_mobile": True,
          "device_scale_factor": 1, "has_touch": True,
          "user_agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                         "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")}
DESKTOP = {"viewport": {"width": 1366, "height": 768}}

# Flags de optimización de Chromium headless para Linux (35W TDP friendly)
CHROMIUM_OPTIMIZED_ARGS = [
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-gpu-compositing",
    "--disable-webgl",
    "--disable-3d-apis",
    "--disable-accelerated-2d-canvas",
    "--disable-accelerated-video-decode",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-extensions",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-translate",
    "--metrics-recording-only",
    "--mute-audio",
    "--no-first-run",
    "--js-flags=--max-old-space-size=512",
]


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Optimiza el consumo de memoria y CPU de Chromium headless."""
    return {"args": CHROMIUM_OPTIMIZED_ARGS}

# Páginas estáticas del sitio (los _posts Jekyll requieren build de Pages — no van acá).
PAGES = ["/", "/funciones.html", "/precios.html", "/servicios.html",
         "/panel.html", "/calculadora.html", "/pulse.html", "/cerebro.html",
         "/casos.html", "/nosotros.html", "/privacidad.html", "/terminos.html", "/blog/",
         "/atencion-whatsapp.html", "/cotizaciones-agendamiento.html", "/seguimiento-equipo.html",
         "/atencion-cliente.html", "/criterios.html", "/cumplimiento.html", "/crm.html", "/salud.html", "/salud-publica.html", "/mercado-publico.html", "/auditoria-contactabilidad.html", "/servicios-pyme.html", "/automotriz.html", "/comercio.html", "/alternativa-crm.html", "/migracion.html",
         "/orquestacion.html", "/confianza.html", "/facil.html", "/inmobiliaria.html"]


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
    """Página con viewport móvil (el default de la suite) + captura de errores JS y de consola."""
    ctx = browser.new_context(**MOBILE)
    page = _install_fast_wait(ctx.new_page())
    page.js_errors = []
    page.on("pageerror", lambda e: page.js_errors.append(str(e)))
    page.on("console", lambda msg: page.js_errors.append(f"Console error: {msg.text}") if msg.type == "error" else None)
    yield page
    ctx.close()


@pytest.fixture(scope="session")
def desktop_page(browser):
    ctx = browser.new_context(**DESKTOP)
    page = _install_fast_wait(ctx.new_page())
    page.js_errors = []
    page.on("pageerror", lambda e: page.js_errors.append(str(e)))
    page.on("console", lambda msg: page.js_errors.append(f"Console error: {msg.text}") if msg.type == "error" else None)
    yield page
    ctx.close()


def _install_fast_wait(page):
    """Acota wait_for_timeout(ms) y evita recargar la misma URL si no mutó el estado."""
    orig_wait = page.wait_for_timeout
    tope = int(os.environ.get("THEIA_MAX_WAIT_MS", "15"))
    page.wait_for_timeout = lambda ms: orig_wait(min(ms, tope))

    orig_goto = page.goto
    orig_set_vp = page.set_viewport_size
    cache = {"url": None, "resp": None, "vp": dict(page.viewport_size or {}), "errs": []}

    def smart_set_vp(vp):
        if cache["vp"] != vp:
            orig_set_vp(vp)
            cache["vp"] = dict(vp)
            cache["url"] = None

    def smart_goto(url, **kw):
        if cache["url"] == url and page.url == url and not page.is_closed():
            body_cls = page.evaluate(
                "() => { window.scrollTo(0, 0); return document.body ? document.body.className : ''; }"
            )
            if "mobile-menu-open" not in body_cls:
                page.js_errors[:] = list(cache["errs"])
                return cache["resp"]
        page.js_errors.clear()
        resp = orig_goto(url, **kw)
        cache["url"] = page.url
        cache["resp"] = resp
        cache["errs"] = list(page.js_errors)
        return resp

    page.set_viewport_size = smart_set_vp
    page.goto = smart_goto
    return page


def pytest_collection_modifyitems(items):
    """Agrupa los tests parametrizados por página dentro de cada archivo para reutilizar el DOM ya cargado."""
    def _sort_key(item):
        spec = getattr(item, "callspec", None)
        if spec:
            for k in ("path", "page_path", "page_name", "subpage"):
                if k in spec.params:
                    return (str(item.fspath), 1, str(spec.params[k]))
        return (str(item.fspath), 0, "")

    items.sort(key=_sort_key)


@pytest.fixture(autouse=True)
def _reset_js_errors(request):
    """Limpia la lista de errores JS y restaura viewports antes de cada test."""
    for fix in ("mobile_page", "desktop_page"):
        if fix in request.fixturenames:
            p = request.getfixturevalue(fix)
            if hasattr(p, "js_errors"):
                p.js_errors.clear()
            if fix == "desktop_page" and hasattr(p, "set_viewport_size"):
                p.set_viewport_size(DESKTOP["viewport"])
            elif fix == "mobile_page" and hasattr(p, "set_viewport_size"):
                p.set_viewport_size(MOBILE["viewport"])


def filtered_js_errors(page):
    """Errores JS reales: se toleran los fallos de RED del widget/analytics
    (el backend TheIA y GA no corren en el server local de tests)."""
    benign = ("Failed to fetch", "NetworkError", "net::ERR", "Load failed",
              "ERR_CONNECTION", "ERR_NAME_NOT_RESOLVED")
    return [e for e in page.js_errors if not any(b in e for b in benign)]
