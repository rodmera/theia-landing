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
      "@keyframes theiaTooltipPulse {" +
        "0%, 100% { transform: translateY(0); }" +
        "50% { transform: translateY(-3px); }" +
      "}" +
      "@media (max-width: 768px) {" +
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

  if (!enhanceWidgetButton()) {
    var retries = 0;
    var iv = setInterval(function () {
      if (enhanceWidgetButton() || ++retries > 20) clearInterval(iv);
    }, 200);
  }
})();
