/* CTA compartido: abre el WebChat propio y conserva WhatsApp como respaldo. */
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

/* Personalización elegante y marketera del botón de WebChat (AI Spark + Tooltip) */
(function () {
  "use strict";

  // Inyectar estilos para el botón dorado y el tooltip flotante
  if (!document.getElementById("theia-widget-custom-style")) {
    var style = document.createElement("style");
    style.id = "theia-widget-custom-style";
    style.textContent =
      "#theia-widget-btn {" +
        "background: linear-gradient(135deg, #d4af37, #ebca73) !important;" +
        "color: #0f172a !important;" +
        "box-shadow: 0 4px 20px rgba(212, 175, 55, 0.45) !important;" +
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
        "box-shadow: 0 8px 28px rgba(212, 175, 55, 0.65) !important;" +
      "}" +
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
    btn.setAttribute("title", "Probar conversación en vivo con TheIA");

    // Inyectar tooltip flotante "Probar conversación en vivo ✨"
    if (!document.getElementById("theia-widget-tooltip")) {
      var tooltip = document.createElement("div");
      tooltip.id = "theia-widget-tooltip";
      tooltip.innerHTML = "Probar conversación en vivo ✨";
      document.body.appendChild(tooltip);

      btn.addEventListener("click", function () {
        if (tooltip) tooltip.style.display = "none";
      });
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
