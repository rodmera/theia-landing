// HU-WEB-033: Homologación Partner de IA y Consola de Reglas
/* CTA compartido (HU-WEB-027): abre el WebChat propio y conserva WhatsApp como respaldo. */
window.openTheiaChat = function openTheiaChat(source) {
  if (typeof window.theiaTrackCTA === 'function') {
    window.theiaTrackCTA('widget-open', source);
  }
  if (typeof window.theiaChatOpen === 'function') {
    window.theiaChatOpen(source);
    return;
  }
  window.open('https://wa.me/12063858350?text=Hola%2C%20quiero%20probar%20TheIA', '_blank');
};

/* Personalización elegante y marketera del botón y frame del WebChat (AI Spark + Contraste Alto + Esquinas Limpias) */
(function () {
  "use strict";

  // Inyectar estilos para el botón dorado, el tooltip y el alto contraste dentro del frame
  if (!document.getElementById("theia-widget-custom-style")) {
    var style = document.createElement("style");
    style.id = "theia-widget-custom-style";
    style.textContent =
      /* Frame Principal - Fondo oscuro #0f172a que elimina píxeles blancos en esquinas con border-radius */
      "#theia-widget-box {" +
        "background: #0f172a !important;" +
        "border-radius: 16px !important;" +
        "overflow: hidden !important;" +
        "border: 1px solid rgba(255, 255, 255, 0.15) !important;" +
        "box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45) !important;" +
      "}" +
      /* Botón Flotante Dorado */
      "#theia-widget-btn {" +
        "background: linear-gradient(135deg, #d4af37, #ebca73) !important;" +
        "color: #0f172a !important;" +
        "box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;" +
        "border: 1px solid rgba(255, 255, 255, 0.4) !important;" +
        "width: 60px !important;" +
        "height: 60px !important;" +
        "border-radius: 50% !important;" +
        "display: flex !important;" +
        "align-items: center !important;" +
        "justify-content: center !important;" +
        "transition: all 0.25s ease !important;" +
      "}" +
      "#theia-widget-btn:hover {" +
        "transform: scale(1.08) translateY(-2px) !important;" +
        "box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45) !important;" +
      "}" +
      /* Tooltip Flotante */
      "#theia-widget-tooltip {" +
        "position: fixed;" +
        "bottom: 32px;" +
        "right: 96px;" +
        "z-index: 9998;" +
        "background: rgba(15, 23, 42, 0.95);" +
        "border: 1px solid rgba(212, 175, 55, 0.5);" +
        "color: #ebca73;" +
        "font-size: 0.82rem;" +
        "font-weight: 700;" +
        "padding: 0.45rem 0.9rem;" +
        "border-radius: 100px;" +
        "box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);" +
        "backdrop-filter: blur(12px);" +
        "pointer-events: none;" +
        "white-space: nowrap;" +
        "font-family: 'Plus Jakarta Sans', system-ui, sans-serif;" +
        "animation: theiaTooltipPulse 2.5s infinite ease-in-out;" +
      "}" +
      /* Estilos Internos del Frame - Alto Contraste */
      "#theia-widget-header {" +
        "background: #0f172a !important;" +
        "color: #ffffff !important;" +
        "border-bottom: 2px solid #d4af37 !important;" +
        "padding: 12px 16px !important;" +
        "border-top-left-radius: 15px !important;" +
        "border-top-right-radius: 15px !important;" +
      "}" +
      "#theia-widget-header span {" +
        "display: flex !important;" +
        "align-items: center !important;" +
        "gap: 8px !important;" +
        "color: #ffffff !important;" +
        "font-weight: 700 !important;" +
      "}" +
      "#theia-widget-header button {" +
        "color: #ebca73 !important;" +
        "opacity: 0.9 !important;" +
      "}" +
      "#theia-widget-header button:hover {" +
        "opacity: 1 !important;" +
        "color: #ffffff !important;" +
      "}" +
      ".theia-quick-replies button {" +
        "background: #0f172a !important;" +
        "color: #ffffff !important;" +
        "border: 1.5px solid #d4af37 !important;" +
        "font-weight: 600 !important;" +
        "padding: 7px 14px !important;" +
        "border-radius: 20px !important;" +
        "box-shadow: 0 2px 8px rgba(15, 23, 42, 0.1) !important;" +
        "transition: all 0.2s ease !important;" +
      "}" +
      ".theia-quick-replies button:hover {" +
        "background: linear-gradient(135deg, #d4af37, #ebca73) !important;" +
        "color: #0f172a !important;" +
        "border-color: #d4af37 !important;" +
        "font-weight: 700 !important;" +
      "}" +
      "#theia-widget-input {" +
        "background: #ffffff !important;" +
        "border-top: 1px solid #e2e8f0 !important;" +
      "}" +
      "#theia-widget-input input {" +
        "border: 1.5px solid #0f172a !important;" +
        "color: #0f172a !important;" +
        "font-weight: 500 !important;" +
      "}" +
      "#theia-widget-input input:focus {" +
        "border-color: #d4af37 !important;" +
        "box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2) !important;" +
      "}" +
      "#theia-widget-input button {" +
        "background: linear-gradient(135deg, #d4af37, #ebca73) !important;" +
        "color: #0f172a !important;" +
        "font-weight: 700 !important;" +
      "}" +
      "#theia-powered {" +
        "background: #0f172a !important;" +
        "color: rgba(255, 255, 255, 0.6) !important;" +
        "border-top: 1px solid rgba(255, 255, 255, 0.1) !important;" +
      "}" +
      "#theia-powered a {" +
        "color: #ebca73 !important;" +
      "}" +
      /* Botón Flotante Oficial de WhatsApp (Esquina Inferior Izquierda) */
      "#theia-wa-float {" +
        "position: fixed !important;" +
        "bottom: 24px !important;" +
        "left: 24px !important;" +
        "z-index: 990 !important;" +
        "width: 52px !important;" +
        "height: 52px !important;" +
        "border-radius: 50% !important;" +
        "background: #25D366 !important;" +
        "color: #ffffff !important;" +
        "box-shadow: 0 4px 14px rgba(37, 211, 102, 0.35) !important;" +
        "display: flex !important;" +
        "align-items: center !important;" +
        "justify-content: center !important;" +
        "text-decoration: none !important;" +
        "transition: transform 0.2s ease, box-shadow 0.2s ease !important;" +
        "cursor: pointer !important;" +
      "}" +
      "#theia-wa-float:hover {" +
        "transform: scale(1.06) translateY(-2px) !important;" +
        "box-shadow: 0 6px 18px rgba(37, 211, 102, 0.45) !important;" +
      "}" +
      "#theia-wa-float svg {" +
        "width: 28px !important;" +
        "height: 28px !important;" +
        "display: block !important;" +
      "}" +
      "@keyframes theiaTooltipPulse {" +
        "0%, 100% { transform: translateY(0); }" +
        "50% { transform: translateY(-3px); }" +
      "}" +
      "@media (max-width: 768px) {" +
        "#theia-wa-float {" +
          "bottom: 20px !important;" +
          "left: 16px !important;" +
        "}" +
        "#theia-widget-tooltip {" +
          "bottom: 88px;" +
          "right: 84px;" +
          "font-size: 0.78rem;" +
          "padding: 0.35rem 0.75rem;" +
        "}" +
      "}";
    document.head.appendChild(style);
  }

  function enhanceWidgetButton() {
    var btn = document.getElementById("theia-widget-btn");
    if (!btn) return false;

    // Sustituir emoji por icono SVG vectorial de AI Spark + Chat
    btn.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0f172a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>' +
        '<path d="M12 7l0.8 1.8 1.8 0.8-1.8 0.8-0.8 1.8-0.8-1.8-1.8-0.8 1.8-0.8z" fill="#0f172a" stroke="none"></path>' +
      '</svg>';
    btn.setAttribute("title", "Chatea con TheIA en vivo");

    // Inyectar tooltip flotante "Chatea con TheIA ✨"
    if (!document.getElementById("theia-widget-tooltip")) {
      var tooltip = document.createElement("div");
      tooltip.id = "theia-widget-tooltip";
      tooltip.innerHTML = "Chatea con TheIA ✨";
      document.body.appendChild(tooltip);

      btn.addEventListener("click", function () {
        if (tooltip) tooltip.style.display = "none";
      });
    }

    // Reemplazar emoji crudo 💬 del header si está presente
    var headerSpan = document.querySelector("#theia-widget-header span");
    if (headerSpan && headerSpan.innerHTML.indexOf("💬") !== -1) {
      headerSpan.innerHTML =
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ebca73" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path><path d="M12 7l0.6 1.4 1.4 0.6-1.4 0.6-0.6 1.4-0.6-1.4-1.4-0.6 1.4-0.6z" fill="#ebca73" stroke="none"></path></svg> ' +
        headerSpan.innerHTML.replace("💬", "").trim();
    }

    return true;
  }

  function injectWhatsAppFloat() {
    if (document.getElementById("theia-wa-float")) return true;
    if (!document.body) return false;

    var a = document.createElement("a");
    a.id = "theia-wa-float";
    a.className = "whatsapp-float-btn";
    a.href = "https://wa.me/12063858350?text=Hola%20TheIA%2C%20quiero%20consultar%20por%20atenci%C3%B3n%20con%20IA";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.setAttribute("aria-label", "Hablar con TheIA por WhatsApp");
    a.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="#ffffff" aria-hidden="true" focusable="false">' +
        '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>' +
        '<path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.5.5 0 00.611.611l4.458-1.495A11.952 11.952 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-2.363 0-4.55-.82-6.274-2.191l-.438-.364-3.2 1.073 1.073-3.2-.364-.438A9.955 9.955 0 012 12C2 6.486 6.486 2 12 2s10 4.486 10 10-4.486 10-10 10z"/>' +
      '</svg>';

    a.addEventListener("click", function () {
      if (typeof window.theiaTrackCTA === "function") {
        window.theiaTrackCTA("whatsapp-float", "floating-btn");
      }
    });

    document.body.appendChild(a);
    return true;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectWhatsAppFloat);
  } else {
    injectWhatsAppFloat();
  }

  if (!enhanceWidgetButton()) {
    var retries = 0;
    var iv = setInterval(function () {
      if (enhanceWidgetButton() || ++retries > 20) clearInterval(iv);
    }, 200);
  }
})();
