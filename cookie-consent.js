/**
 * Cookie Consent Banner — TheIA.cl
 * Bloquea GA4 y Meta Pixel hasta que el usuario acepte.
 * Cumplimiento Ley 21.719 (Art. 12: consentimiento libre, informado, específico e inequívoco).
 */
(function () {
  "use strict";

  var COOKIE_NAME = "theia_cookie_consent";
  var GA_ID = "G-37L5WMXF83";
  var META_ID = "2143491406057008";

  function getConsent() {
    var match = document.cookie.match(new RegExp("(?:^|; )" + COOKIE_NAME + "=([^;]*)"));
    return match ? decodeURIComponent(match[1]) : null;
  }

  function setConsent(value) {
    var expires = new Date(Date.now() + 365 * 864e5).toUTCString();
    document.cookie = COOKIE_NAME + "=" + value + "; expires=" + expires + "; path=/; SameSite=Lax; Secure";
  }

  function loadGA4() {
    if (document.getElementById("theia-ga4")) return;
    var s = document.createElement("script");
    s.id = "theia-ga4";
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    gtag("js", new Date());
    gtag("config", GA_ID);
  }

  function loadMetaPixel() {
    if (window.fbq) return;
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
      };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0";
      n.queue = []; t = b.createElement(e); t.async = !0;
      t.src = v; s = b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t, s);
    }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    fbq("init", META_ID);
    fbq("track", "PageView");
  }

  function enableTracking() {
    loadGA4();
    loadMetaPixel();
  }

  function hideBanner() {
    var el = document.getElementById("theia-cookie-banner");
    if (el) el.remove();
  }

  function showBanner() {
    var banner = document.createElement("div");
    banner.id = "theia-cookie-banner";
    banner.innerHTML =
      '<div style="max-width:900px;margin:0 auto;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">' +
        '<p style="flex:1;min-width:200px;margin:0;font-size:0.85rem;line-height:1.5;">Este sitio usa cookies de analytics y marketing para mejorar tu experiencia. ' +
          '<a href="/privacidad" style="color:#ebca73;text-decoration:underline;">Política de privacidad</a></p>' +
        '<div style="display:flex;gap:0.5rem;flex-shrink:0;">' +
          '<button id="theia-cc-reject" style="background:transparent;color:rgba(255,255,255,0.7);border:1px solid rgba(255,255,255,0.2);padding:0.5rem 1.1rem;border-radius:8px;font-size:0.82rem;font-weight:600;cursor:pointer;font-family:inherit;transition:all 0.2s;">Rechazar</button>' +
          '<button id="theia-cc-accept" style="background:linear-gradient(135deg,#d4af37,#ebca73);color:#0f172a;border:none;padding:0.5rem 1.1rem;border-radius:8px;font-size:0.82rem;font-weight:700;cursor:pointer;font-family:inherit;transition:all 0.2s;">Aceptar</button>' +
        '</div>' +
      '</div>';

    banner.style.cssText =
      "position:fixed;bottom:0;left:0;right:0;z-index:10000;" +
      "background:rgba(15,23,42,0.97);backdrop-filter:blur(12px);" +
      "border-top:1px solid rgba(255,255,255,0.12);" +
      "padding:1rem 1.5rem;font-family:'Plus Jakarta Sans',system-ui,sans-serif;color:#fff;";

    document.body.appendChild(banner);

    document.getElementById("theia-cc-accept").addEventListener("click", function () {
      setConsent("accepted");
      enableTracking();
      hideBanner();
    });

    document.getElementById("theia-cc-reject").addEventListener("click", function () {
      setConsent("rejected");
      hideBanner();
    });
  }

  // Lógica principal
  var consent = getConsent();
  if (consent === "accepted") {
    enableTracking();
  } else if (consent !== "rejected") {
    // Sin decisión previa — mostrar banner
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", showBanner);
    } else {
      showBanner();
    }
  }
  // Si rejected: no hacer nada (no cargar tracking, no mostrar banner)
})();
