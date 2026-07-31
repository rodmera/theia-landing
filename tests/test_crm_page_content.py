"""Contratos de copy y coherencia de la página CRM (HU-WEB-012).

La página CRM es la preview honesta de las capacidades implementadas
(HU-CRM-001 a 005). NO debe prometer features en backlog: tareas
(CRM-012), cotizaciones (CRM-027), reportes (CRM-029), cierre
(CRM-011), timeline (CRM-008), campos personalizados (CRM-006),
responsable (CRM-009). Si una feature no está en producción, no
aparece en el copy.

Reglas duras adicionales (2026-07-30, mini-revisión):
- No IDs HU visibles en el HTML público (trazabilidad vive en el vault).
- No aparece "pipeline" ni "tenant" (jerga startup).
- No aparece "Cerrado" (la columna del kanban usa "Esperando respuesta").
- El H1 incorpora "CRM" sin perder "agenda de clientes" (claim A).
- La página carga el helper compartido /webchat-cta.js antes del widget.
- El bloque "qué viene después" no apunta a una URL pública futura
  (la HU-WEB-019 es una nota de vault, no una URL pública).
- No hay precio público (HU-WEB-014 está bloqueada por HU-CRM-036).
- No hay reclamos de reporte/cierre de negocio en copy visible.
- Los CTAs usan openTheiaChat('crm').
- Las features mencionadas coinciden con CRM-001 a 005.
"""
import re
from pathlib import Path

import pytest

from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
CRM_PAGE = ROOT / "crm.html"
FUNCIONES_PAGE = ROOT / "funciones.html"
PRECIOS_PAGE = ROOT / "precios.html"

# Cosas que NO pueden aparecer en copy visible de crm.html.
JERGA_FORBIDDEN = [
    "pipeline",
    "tenant",
]

# Estados del kanban: "Cerrado" suena a cierre de negocio
# (CRM-011, que está en backlog). Usamos "Esperando respuesta".
ETAPA_FORBIDDEN = ["cerrado"]


def _visible_source(html):
    """Extrae texto visible (sin <script>, <style>, comentarios, JSON-LD)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    return html


# ─────────────────────────── crm.html ───────────────────────────

def test_crm_page_existe():
    assert CRM_PAGE.is_file(), "crm.html no existe en la raíz del repo"


def test_crm_page_no_promete_features_fuera_de_produccion():
    """Las 7 features en backlog NO deben aparecer en el copy visible de crm.html."""
    source = _visible_source(CRM_PAGE.read_text(encoding="utf-8")).lower()
    forbidden = [
        "tareas", "cotizaciones", "reportes", "ganado", "perdido",
        "timeline", "próximamente", "soon", "avísame",
    ]
    findings = [w for w in forbidden if w in source]
    assert not findings, (
        f"crm.html menciona palabras de features en backlog: {findings}. "
        "Si la feature está en producción, sácala del contrato y actualiza la lista."
    )


def test_crm_page_no_usa_jerga_startup():
    """Palabras de jerga startup no entran en copy visible de crm.html."""
    source = _visible_source(CRM_PAGE.read_text(encoding="utf-8")).lower()
    findings = [w for w in JERGA_FORBIDDEN if w in source]
    assert not findings, f"crm.html usa jerga startup: {findings}"


def test_crm_page_no_muestra_etapa_cerrado():
    """'Cerrado' suena a cierre de negocio (CRM-011, backlog). Etapas honestas."""
    source = _visible_source(CRM_PAGE.read_text(encoding="utf-8")).lower()
    findings = [w for w in ETAPA_FORBIDDEN if w in source]
    assert not findings, (
        f"crm.html usa {findings} como etapa. 'Cerrado' implica cierre de negocio "
        "(CRM-011, backlog). Usa 'Esperando respuesta' u otro estado honesto."
    )


def test_crm_page_no_muestra_ids_hu_visibles():
    """No IDs HU en el HTML público. La trazabilidad vive en el vault."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    findings = re.findall(r"HU-CRM-\d{3}", source)
    assert not findings, (
        f"crm.html expone IDs HU en el HTML: {findings}. "
        "La trazabilidad vive en el vault; el HTML público no debe citarla."
    )


def test_crm_page_no_apunta_a_url_futura_de_hu_web_019():
    """No hay promesa de URL pública para HU-WEB-019 (es nota de vault, no ruta)."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    # Cualquier href que mencione "hu-web-019" o un placeholder roto.
    bad = re.findall(r'href="[^"]*hu-web-019[^"]*"', source, re.I)
    assert not bad, f"crm.html enlaza a HU-WEB-019 como URL: {bad}"
    # Y el atributo data-hu-crm-placeholder tampoco debe quedar.
    assert "data-hu-crm-placeholder" not in source, (
        "crm.html aún tiene el atributo data-hu-crm-placeholder; "
        "no hay URL pública para esa nota de vault."
    )


def test_crm_page_carga_webchat_cta():
    """El helper compartido /webchat-cta.js debe cargarse antes del widget."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    assert 'src="/webchat-cta.js"' in source, (
        "crm.html no carga /webchat-cta.js. El helper openTheiaChat debe "
        "registrar widget-open, abrir el WebChat y caer a WhatsApp."
    )
    # El helper va antes del widget.
    assert source.index("/webchat-cta.js") < source.index("webchat-widget.js"), (
        "crm.html carga /webchat-cta.js después del widget; "
        "el helper debe estar disponibles antes de cualquier onclick."
    )


def test_crm_page_usa_openTheiaChat_crm():
    """Los CTAs de la página CRM usan el helper compartido openTheiaChat('crm')."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('crm')" in source, "crm.html no llama openTheiaChat('crm')"
    assert "theiaChatOpen('crm')" not in source, (
        "crm.html aún tiene la forma inline theiaChatOpen('crm'); "
        "usa el helper compartido openTheiaChat"
    )


def test_crm_page_muestra_las_5_features_de_crm_001_a_005():
    """Las 5 features implementadas (CRM-001 a 005) deben estar mencionadas."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    keywords = ["Negocios", "Etapas", "Se enciende", "Kanban",
                "actualiza desde la conversación"]
    missing = [k for k in keywords if k not in source]
    assert not missing, f"crm.html no menciona features implementadas: {missing}"


def test_crm_page_no_tiene_imagenes_con_alt_reporte():
    """Sin capturas de 'reporte' (no hay reportes en producción)."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    bad = re.findall(r'<img[^>]*alt="[^"]*reporte[^"]*"', source, re.I)
    assert not bad, f"crm.html tiene <img> con alt que contiene 'reporte': {bad}"


def test_crm_page_h1_incluye_crm_y_agenda_de_clientes():
    """El H1 lleva 'CRM' (SEO) y 'agenda de clientes' (claim A, lenguaje del dueño)."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    m = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.DOTALL | re.I)
    assert m, "crm.html sin <h1>"
    h1 = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
    assert "crm" in h1.lower(), f"H1 no menciona 'CRM' (SEO): {h1!r}"
    assert "agenda de clientes" in h1.lower(), (
        f"H1 no menciona 'agenda de clientes' (claim A): {h1!r}"
    )


def test_crm_page_no_promete_precio():
    """crm.html NO muestra cifras de precio. Desde 2026-07-30 el CRM va incluido en
    la mensualidad, así que la página tampoco debe repetir el monto del plan: el
    precio se declara en un solo lugar (precios.html) para no volver a desalinearse."""
    source = CRM_PAGE.read_text(encoding="utf-8").lower()
    forbidden = ["$190.000", "190.000", "$250.000", "250.000", "clp 190", "clp 250", "usd", "precio mens"]
    findings = [w for w in forbidden if w in source]
    assert not findings, f"crm.html promete precio público: {findings}"


def test_crm_page_no_muestra_cierre_ganado_perdido():
    """El módulo no tiene 'cierre' de negocio en producción."""
    source = _visible_source(CRM_PAGE.read_text(encoding="utf-8")).lower()
    forbidden = ["cierre", "ganado", "perdido"]
    findings = [w for w in forbidden if w in source]
    assert not findings, (
        f"crm.html muestra copy de cierre/ganado/perdido: {findings}. "
        "Eso pertenece a HU-CRM-011 (backlog)."
    )


def test_crm_page_no_confunde_kanban_con_reporte():
    """El tablero muestra etapas; no promete medición o reportes en backlog."""
    source = _visible_source(CRM_PAGE.read_text(encoding="utf-8")).lower()
    assert "cuántos negocios pasan por tus etapas" not in source, (
        "crm.html transforma el kanban en una promesa de medición. "
        "La página debe limitarse a ver y mover negocios por etapas."
    )


def test_crm_page_ficha_solo_datos_respaldados_por_crm_001_005():
    """La ficha del negocio no muestra campos que no estén en CRM-001 a 005.
    Sin 'Última interacción' (sería CRM-008 timeline), 'Resumen' (no existe),
    'historial' (idem). Solo nombre, etapa y canal están respaldados."""
    source = _visible_source(CRM_PAGE.read_text(encoding="utf-8"))
    forbidden = ["Última interacción", "Resumen", "historial"]
    findings = [w for w in forbidden if w in source]
    assert not findings, (
        f"crm.html menciona {findings} en la ficha. Esos campos no están "
        "respaldados por HU-CRM-001 a 005 (timeline = CRM-008, en backlog)."
    )


def test_crm_page_no_promete_pago_previo():
    """El feature 'Se enciende cuando lo necesitas' no puede prometer pago antes.
    HU-WEB-014 y HU-CRM-036 siguen en backlog — no hay empaquetado/precio aprobado."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    forbidden = ["pagarlo antes", "pagar antes", "te obliga a pagar", "ni te obliga"]
    findings = [w for w in forbidden if w in source]
    assert not findings, (
        f"crm.html promete pago/empaquetado: {findings}. "
        "Esas promesas viven en HU-WEB-014 / HU-CRM-036, ambas en backlog."
    )


def test_crm_page_incluye_captura_real_del_kanban():
    """AC2 (redefinido 2026-07-30): la página prueba con la captura real del
    kanban, no con mockups HTML en el DOM."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    # Captura real del producto (anonimizada, versionada).
    assert 'src="screenshots/crm-kanban.png"' in source, (
        "crm.html sin captura real del kanban. AC2 lo exige."
    )
    # El mockup HTML del kanban NO debe quedar en el DOM.
    for forbidden in ["board-cols", "board-col ", "board-card ", "board-card-name"]:
        assert forbidden not in source, (
            f"crm.html aún tiene el mockup HTML del kanban ('{forbidden}'). "
            "AC2: reemplaza por capturas reales, no por réplicas en el DOM."
        )
    # La captura referenciada existe en disco.
    kanban = ROOT / "screenshots/crm-kanban.png"
    assert kanban.is_file(), f"falta {kanban}"


def test_crm_page_no_publica_ficha_de_negocio():
    """AC2 (redefinido 2026-07-30): el producto NO tiene vista de detalle de
    negocio — solo detalle de contacto, que muestra timeline, inteligencia,
    recordatorios y marcar cliente/perdido: features que AC1 prohíbe prometer.
    Publicar esa pantalla como 'ficha de negocio' engaña al visitante.

    Contrafactual: si alguien vuelve a agregar una captura de ficha o el mockup
    HTML equivalente, este test falla. Reactivar solo cuando el producto tenga
    una vista real de detalle de negocio (ver HU-WEB-019)."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    assert "crm-deal.png" not in source, (
        "crm.html referencia una captura de ficha de negocio. Esa pantalla no "
        "existe en el producto: la captura disponible es el detalle de CONTACTO "
        "y expone features fuera de alcance (timeline, recordatorios, perdido)."
    )
    for forbidden in ["deal-header", "deal-avatar", "deal-row", "deal-row-label"]:
        assert forbidden not in source, (
            f"crm.html tiene el mockup HTML de la ficha ('{forbidden}'). "
            "AC2: sin vista real de negocio en el producto, no se maqueta una."
        )


def test_captura_crm_tiene_ampliacion_accesible_en_movil(mobile_page):
    """En móvil, la captura panorámica se puede abrir completa y con etiqueta."""
    mobile_page.goto(BASE + "/crm.html", wait_until="domcontentloaded")

    link = mobile_page.get_by_role("link", name="Ampliar captura del kanban")
    assert link.get_attribute("href") == "screenshots/crm-kanban.png"
    assert link.get_attribute("target") == "_blank"
    assert link.get_attribute("rel") == "noopener"


def test_reveal_queda_visible_al_hacer_scroll_en_movil(mobile_page):
    """Las animaciones .reveal se activan al hacer scroll en móvil.
    Verifica que un .reveal en una sección no inicial queda con opacity=1
    cuando el viewport lo observa."""
    mobile_page.goto(BASE + "/crm.html", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(400)
    target = mobile_page.locator(".features .reveal").first
    target.scroll_into_view_if_needed()
    # Transición CSS: opacity 0.5s + delay 0..N*60ms. Damos 1500ms.
    mobile_page.wait_for_timeout(1500)
    opacity = target.evaluate("el => getComputedStyle(el).opacity")
    assert opacity == "1", (
        f"el .reveal de la sección features no quedó visible tras scroll: opacity={opacity}"
    )
    # El atributo class debe incluir 'visible' (marcado por IntersectionObserver).
    classes = target.evaluate("el => el.className")
    assert "visible" in classes, (
        f"el .reveal no recibió la clase 'visible' tras scroll: classes={classes!r}"
    )


def test_cta_crm_abre_webchat_con_origen_estable(mobile_page):
    """Al hacer click, el CTA usa el contrato público del helper con source=crm."""
    mobile_page.goto(BASE + "/crm.html", wait_until="domcontentloaded")
    mobile_page.evaluate("""
        window.__crmCtaEvents = [];
        window.theiaTrackCTA = (event, source) => window.__crmCtaEvents.push([event, source]);
        window.theiaChatOpen = source => window.__crmCtaEvents.push(["chat-open", source]);
    """)
    # El widget puede inicializarse y abrirse sin source. Esperamos ese efecto
    # externo y aislamos el click que es el comportamiento bajo contrato.
    mobile_page.wait_for_timeout(600)
    mobile_page.evaluate("window.__crmCtaEvents = []")

    mobile_page.get_by_role("button", name="Habla con TheIA").first.click()

    assert mobile_page.evaluate("window.__crmCtaEvents") == [
        ["widget-open", "crm"],
        ["chat-open", "crm"],
    ]


# ──────────────── navegación de productos enlaza a CRM ────────────────

@pytest.mark.parametrize(
    "path",
    [ROOT / "index.html", FUNCIONES_PAGE, PRECIOS_PAGE, ROOT / "pulse.html",
     ROOT / "plataforma.html"],
)
def test_pagina_enlaza_a_crm(path):
    """La navegación de las páginas de producto lleva al módulo CRM."""
    source = path.read_text(encoding="utf-8")
    m = re.search(r'<a[^>]+href="(/crm(?:[\.html]?|/)?)"[^>]*>[^<]*</a>', source, re.I)
    assert m, (
        f"{path.name} no enlaza al módulo CRM (/crm). "
        "El producto CRM debe estar navegable desde las páginas de producto."
    )
