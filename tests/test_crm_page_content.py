"""Contratos de copy y coherencia de la página CRM Completa (HU-WEB-019).

La página CRM de TheIA describe la solución CRM completa con las 6
capacidades habilitadas en producción:
- HU-CRM-006: Campos personalizados
- HU-CRM-008: Timeline e historial unificado
- HU-CRM-011: Cierre ganado/perdido con motivo
- HU-CRM-012: Tareas de venta (agenda del vendedor)
- HU-CRM-027: Cotizaciones ligadas al negocio
- HU-CRM-029: Reportes de ventas e indicadores

Reglas duras:
- No IDs HU visibles como texto para el usuario (la trazabilidad vive en atributos data-hu-crm).
- No aparece "pipeline" ni "tenant" (jerga startup).
- El H1 incorpora "CRM" y "agenda de clientes" (claim A).
- La página carga el helper compartido /webchat-cta.js antes del widget.
- Ya NO existe el placeholder "qué viene después" de la preview (HU-WEB-012).
- No hay precio público (HU-WEB-014 está bloqueada por HU-CRM-036).
- Los CTAs usan openTheiaChat('crm').
- Las features mencionadas tienen atribución explícita vía atributos data-hu-crm="HU-CRM-xxx".
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


def _visible_source(html):
    """Extrae texto visible (sin <script>, <style>, comentarios, JSON-LD y elimina atributos en tags)."""
    for tag in ("script", "style"):
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    # Eliminar definiciones de tags e HTML attributes para dejar solo texto interno
    html = re.sub(r"<[^>]+>", " ", html)
    return html


# ─────────────────────────── crm.html ───────────────────────────

def test_crm_page_existe():
    assert CRM_PAGE.is_file(), "crm.html no existe en la raíz del repo"


def test_crm_page_incluye_todas_las_features_de_crm_completas():
    """HU-WEB-019: La página CRM debe incluir las 6 features en producción."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    required_hu_tags = [
        "HU-CRM-001",  # Negocios / Embudo
        "HU-CRM-006",  # Campos personalizados
        "HU-CRM-008",  # Timeline / Historial
        "HU-CRM-011",  # Cierre ganado/perdido
        "HU-CRM-012",  # Tareas de venta
        "HU-CRM-027",  # Cotizaciones
        "HU-CRM-029",  # Reportes
    ]
    missing = [tag for tag in required_hu_tags if f'data-hu-crm="{tag}"' not in source]
    assert not missing, f"crm.html no tiene atribución data-hu-crm para las features: {missing}"


def test_crm_page_no_usa_jerga_startup():
    """Palabras de jerga startup no entran en copy visible de crm.html."""
    source = _visible_source(CRM_PAGE.read_text(encoding="utf-8")).lower()
    findings = [w for w in JERGA_FORBIDDEN if w in source]
    assert not findings, f"crm.html usa jerga startup: {findings}"


def test_crm_page_no_muestra_ids_hu_como_texto_visible():
    """No IDs HU visibles en el texto. La trazabilidad usa atributos data-hu-crm."""
    visible = _visible_source(CRM_PAGE.read_text(encoding="utf-8"))
    findings = re.findall(r"HU-CRM-\d{3}", visible)
    assert not findings, (
        f"crm.html expone IDs HU en el texto visible: {findings}. "
        "Usa atributos data-hu-crm='HU-CRM-xxx', no texto visible."
    )


def test_crm_page_no_tiene_placeholder_que_viene_despues():
    """HU-WEB-019: Se elimina la tarjeta placeholder 'qué viene después'."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    assert "Qué viene después" not in source, (
        "crm.html aún conserva la sección 'Qué viene después' de la preview. "
        "HU-WEB-019: reemplaza el placeholder con las secciones completas de CRM."
    )
    assert "data-hu-crm-placeholder" not in source, (
        "crm.html conserva el atributo data-hu-crm-placeholder."
    )


def test_crm_page_carga_webchat_cta():
    """El helper compartido /webchat-cta.js debe cargarse antes del widget."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    assert 'src="/webchat-cta.js"' in source, (
        "crm.html no carga /webchat-cta.js. El helper openTheiaChat debe "
        "registrar widget-open, abrir el WebChat y caer a WhatsApp."
    )
    assert source.index("/webchat-cta.js") < source.index("webchat-widget.js"), (
        "crm.html carga /webchat-cta.js después del widget; "
        "el helper debe estar disponible antes de cualquier onclick."
    )


def test_crm_page_usa_openTheiaChat_crm():
    """Los CTAs de la página CRM usan el helper compartido openTheiaChat('crm')."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    assert "openTheiaChat('crm')" in source, "crm.html no llama openTheiaChat('crm')"
    assert "theiaChatOpen('crm')" not in source, (
        "crm.html aún tiene la forma inline theiaChatOpen('crm'); "
        "usa el helper compartido openTheiaChat"
    )


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
    """crm.html NO muestra cifras de precio. El CRM va incluido en la mensualidad."""
    source = CRM_PAGE.read_text(encoding="utf-8").lower()
    forbidden = ["$190.000", "190.000", "$250.000", "250.000", "clp 190", "clp 250", "usd", "precio mens"]
    findings = [w for w in forbidden if w in source]
    assert not findings, f"crm.html promete precio público: {findings}"


def test_crm_page_vocabularios_de_las_6_features():
    """El HTML debe incluir vocabulario reconocible de las 6 features."""
    source = CRM_PAGE.read_text(encoding="utf-8").lower()
    vocabularies = [
        ("campos personalizados", ["campos personalizados", "campos del negocio"]),
        ("timeline", ["historial", "timeline", "actividad"]),
        ("cierre", ["ganado", "perdido", "motivo de cierre"]),
        ("tareas", ["tareas", "agenda", "recordatorio"]),
        ("cotizaciones", ["cotizaciones", "cotizar"]),
        ("reportes", ["reportes", "métricas", "indicadores"]),
    ]
    missing = []
    for feature_name, terms in vocabularies:
        if not any(term in source for term in terms):
            missing.append(feature_name)
    assert not missing, f"crm.html no contiene vocabulario de las features: {missing}"


def test_crm_page_imagenes_tienen_alt_descriptivo():
    """Las imágenes de la página CRM tienen alt descriptivo sin referencias rotas."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    imgs = re.findall(r'<img[^>]*>', source, re.I)
    for img in imgs:
        assert 'alt="' in img, f"Imagen sin alt: {img}"
        assert 'alt=""' not in img, f"Imagen con alt vacío: {img}"


def test_cta_crm_abre_webchat_con_origen_estable(mobile_page):
    """Al hacer click, el CTA usa el contrato público del helper con source=crm."""
    mobile_page.goto(BASE + "/crm.html", wait_until="domcontentloaded")
    mobile_page.evaluate("""
        window.__crmCtaEvents = [];
        window.theiaTrackCTA = (event, source) => window.__crmCtaEvents.push([event, source]);
        window.theiaChatOpen = source => window.__crmCtaEvents.push(["chat-open", source]);
    """)
    mobile_page.wait_for_timeout(600)
    mobile_page.evaluate("window.__crmCtaEvents = []")

    mobile_page.get_by_role("button", name="Probar conversación en vivo").first.click()

    assert mobile_page.evaluate("window.__crmCtaEvents") == [
        ["widget-open", "crm"],
        ["chat-open", "crm"],
    ]


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
