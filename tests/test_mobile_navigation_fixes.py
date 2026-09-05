"""
Tests E2E Playwright Mobile (iPhone 14) para corrección de navegación móvil (HU-WEB-027).
Verifica:
- AC1: Enlace canónico a CRM en home y atencion-cliente (<a> con href="/crm", sin onclick).
- AC2: Menú móvil limpio con exactamente un solo enlace a Nosotros en el drawer.
- AC3: Navegación táctil confiable a /nosotros en viewport móvil cerrando el drawer.
- AC4: Emulación iPhone 14 (390x844), cero errores JS, cero overflow horizontal y status 200.
"""
from pathlib import Path
import pytest
from conftest import BASE, ROOT, filtered_js_errors

INDEX_HTML = ROOT / "index.html"
ATENCION_HTML = ROOT / "atencion-cliente.html"

# Todas las 25 páginas con site-nav
ALL_PAGES_WITH_NAV = [
    f.name for f in ROOT.glob("*.html")
    if f.name != "plataforma.html" and "site-nav" in f.read_text(encoding="utf-8")
]


def test_t1_crm_action_is_canonical_link_not_button():
    """HU-WEB-027 AC1: La tarjeta CRM en .product-suite-grid debe ser un <a> con href='/crm', sin onclick."""
    for html_file in [INDEX_HTML, ATENCION_HTML]:
        content = html_file.read_text(encoding="utf-8")
        # No debe existir ningún button con openTheiaChat('crm')
        assert "openTheiaChat('crm')" not in content, (
            f"{html_file.name} contiene botón con openTheiaChat('crm') en vez de enlace canónico"
        )
        assert 'href="/crm"' in content, f"{html_file.name} debe contener enlace canónico href='/crm'"


def test_t2_mobile_click_conocer_crm_navigates_to_crm(mobile_page):
    """HU-WEB-027 AC1, AC4: Al pulsar 'Conocer CRM →' en atencion-cliente móvil se navega a /crm con status 200."""
    mobile_page.goto(f"{BASE}/atencion-cliente.html", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    # Buscar el enlace específico de la tarjeta CRM
    crm_action = mobile_page.locator(".product-suite-card__action[href='/crm']")
    assert crm_action.count() >= 1, "Enlace .product-suite-card__action con href='/crm' no encontrado en atencion-cliente"

    crm_action.first.scroll_into_view_if_needed()
    crm_action.first.click()
    mobile_page.wait_for_url(lambda u: "/crm" in u or "/crm.html" in u, timeout=5000)

    # Verificar que el h1 o título de CRM esté presente
    h1 = mobile_page.locator("h1")
    assert h1.is_visible(), "Página /crm debe cargar con <h1> visible"
    assert len(filtered_js_errors(mobile_page)) == 0, "Cero errores JS tras navegar a CRM"


def test_t3_click_conocer_crm_does_not_open_webchat(mobile_page):
    """HU-WEB-027 AC1: Pulsar 'Conocer CRM →' debe navegar nativamente sin invocar openTheiaChat."""
    mobile_page.goto(f"{BASE}/atencion-cliente.html", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    crm_action = mobile_page.locator(".product-suite-card__action[href='/crm']").first
    assert crm_action.is_visible()
    # Verificar que no tiene handler onclick ni llama a openTheiaChat
    assert crm_action.get_attribute("onclick") is None
    assert crm_action.get_attribute("href") == "/crm"

    # Verificar que es un tag <a> nativo
    tag_name = crm_action.evaluate("el => el.tagName")
    assert tag_name == "A", "La acción de CRM debe ser un enlace <a>"


def test_t4_single_nosotros_link_visible_in_mobile_drawer(mobile_page):
    """HU-WEB-027 AC2: En viewport móvil, debe existir exactamente UN solo enlace a Nosotros visible en el drawer."""
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    # Abrir menú hamburguesa
    menu_toggle = mobile_page.locator(".menu-toggle")
    assert menu_toggle.is_visible(), "Botón hamburguesa .menu-toggle debe ser visible en móvil"
    menu_toggle.click()
    mobile_page.wait_for_timeout(300)

    # Contar enlaces a /nosotros dentro del nav que sean visibles
    nosotros_links = mobile_page.locator(".site-nav a[href='/nosotros']")
    total_count = nosotros_links.count()
    assert total_count >= 1, "Debe existir al menos un enlace a /nosotros en el DOM"

    visible_count = 0
    for i in range(total_count):
        if nosotros_links.nth(i).is_visible():
            visible_count += 1

    assert visible_count == 1, (
        f"Debe haber exactamente 1 enlace a Nosotros visible en móvil, pero se encontraron {visible_count}"
    )


def test_t5_mobile_click_nosotros_navigates_and_closes_drawer(mobile_page):
    """HU-WEB-027 AC3, AC4: Clic en 'Nosotros' en el drawer móvil navega a /nosotros y cierra el menú."""
    mobile_page.goto(f"{BASE}/", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(200)

    menu_toggle = mobile_page.locator(".menu-toggle")
    menu_toggle.click()
    mobile_page.wait_for_timeout(300)

    # Clic en el enlace visible a Nosotros
    nosotros_link = mobile_page.locator(".site-nav__mobile-links a[href='/nosotros']")
    assert nosotros_link.is_visible(), "El enlace categorizado a Nosotros debe ser visible en el drawer móvil"
    nosotros_link.click()

    mobile_page.wait_for_url(lambda u: "/nosotros" in u or "/nosotros.html" in u, timeout=5000)

    # Verificar que el h1 esté presente
    h1 = mobile_page.locator("h1")
    assert h1.is_visible(), "Página /nosotros debe cargar con <h1> visible"

    # Verificar que el body no tenga mobile-menu-open tras navegar
    body_classes = mobile_page.locator("body").get_attribute("class") or ""
    assert "mobile-menu-open" not in body_classes, "El drawer debe cerrarse tras navegar"


def test_t6_no_horizontal_overflow_mobile(mobile_page):
    """HU-WEB-027 AC4: Cero overflow horizontal en home, /crm y /nosotros."""
    for path in ["/", "/crm", "/nosotros"]:
        mobile_page.goto(f"{BASE}{path}", wait_until="domcontentloaded")
        mobile_page.wait_for_timeout(200)

        scroll_w = mobile_page.evaluate("document.documentElement.scrollWidth")
        client_w = mobile_page.evaluate("document.documentElement.clientWidth")
        assert scroll_w <= client_w, f"Overflow horizontal detectado en {path}: scrollWidth={scroll_w} > clientWidth={client_w}"


@pytest.mark.parametrize("page_name", ALL_PAGES_WITH_NAV)
def test_t8_homologation_single_nosotros_visible_across_all_pages(mobile_page, page_name):
    """HU-WEB-027 AC2, AC4: Homologación en las 25 páginas con nav — exactamente 1 enlace a Nosotros visible en drawer móvil."""
    mobile_page.goto(f"{BASE}/{page_name}", wait_until="domcontentloaded")
    mobile_page.wait_for_timeout(150)

    menu_toggle = mobile_page.locator(".menu-toggle")
    if menu_toggle.is_visible():
        menu_toggle.click(force=True)
        mobile_page.wait_for_timeout(200)

        nosotros_links = mobile_page.locator(".site-nav a[href='/nosotros']")
        total = nosotros_links.count()
        visible_count = sum(1 for i in range(total) if nosotros_links.nth(i).is_visible())
        assert visible_count == 1, (
            f"En {page_name} debe haber exactamente 1 enlace a Nosotros visible en móvil, encontrados {visible_count}"
        )
