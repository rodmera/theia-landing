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

/* Modal de Agendamiento In-Site (Retención de Leads sin redirigir fuera de theia.cl) */
window.openTheiaDemoModal = function openTheiaDemoModal(source) {
  if (typeof window.theiaTrackCTA === 'function') {
    window.theiaTrackCTA('demo', source || 'modal');
  }

  var existing = document.getElementById("theia-demo-modal");
  if (existing) {
    existing.style.display = "flex";
    setTimeout(function () { existing.style.opacity = "1"; }, 10);
    return;
  }

  var modal = document.createElement("div");
  modal.id = "theia-demo-modal";
  modal.innerHTML =
    '<div class="theia-demo-container">' +
      '<div class="theia-demo-header">' +
        '<div>' +
          '<div style="font-size:0.75rem; font-weight:700; color:#ebca73; text-transform:uppercase; letter-spacing:0.05em;">Demostración Personalizada</div>' +
          '<h3 style="margin:0.15rem 0 0; font-family:\'Merriweather\',serif; font-size:1.1rem; color:#ffffff;">Agenda una Demo de 30 minutos</h3>' +
        '</div>' +
        '<div style="display:flex; align-items:center; gap:0.75rem;">' +
          '<a href="https://calendar.app.google/ZDjEtqCXTJVxzi7bA" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.6); font-size:0.8rem; text-decoration:underline;">Nueva pestaña ↗</a>' +
          '<button id="theia-demo-close" aria-label="Cerrar" style="background:none; border:none; color:#ebca73; font-size:1.8rem; cursor:pointer; line-height:1; padding:0 4px;">&times;</button>' +
        '</div>' +
      '</div>' +
      '<iframe src="https://calendar.app.google/ZDjEtqCXTJVxzi7bA" title="Agenda Demo TheIA"></iframe>' +
    '</div>';

  document.body.appendChild(modal);
  setTimeout(function () { modal.style.opacity = "1"; }, 10);

  function closeModal() {
    modal.style.opacity = "0";
    setTimeout(function () { modal.style.display = "none"; }, 250);
  }

  document.getElementById("theia-demo-close").addEventListener("click", closeModal);
  modal.addEventListener("click", function (e) {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modal.style.display !== "none") closeModal();
  });
};

/* Interceptar clics en enlaces de demo para abrir el modal in-site */
document.addEventListener("click", function (e) {
  var target = e.target.closest("a[href*='calendar.app.google']");
  if (target) {
    e.preventDefault();
    var sourceAttr = target.getAttribute("onclick") || "";
    var match = sourceAttr.match(/'demo'\s*,\s*'([^']+)'/);
    var sourceTag = match ? match[1] : "site-link";
    window.openTheiaDemoModal(sourceTag);
  }
});

/* Personalización elegante y marketera del botón y frame del WebChat (AI Spark + Contraste Alto + Esquinas Limpias) */
(function () {
  "use strict";

  // Inyectar estilos para el botón dorado, el tooltip, el modal de agendamiento y el alto contraste dentro del frame
  if (!document.getElementById("theia-widget-custom-style")) {
    var style = document.createElement("style");
    style.id = "theia-widget-custom-style";
    style.textContent =
      /* Modal de Agendamiento In-Site */
      "#theia-demo-modal {" +
        "position: fixed; top: 0; left: 0; right: 0; bottom: 0;" +
        "background: rgba(15, 23, 42, 0.88);" +
        "backdrop-filter: blur(12px);" +
        "z-index: 10005;" +
        "display: flex; align-items: center; justify-content: center;" +
        "opacity: 0; transition: opacity 0.25s ease;" +
        "padding: 1rem;" +
        "box-sizing: border-box;" +
      "}" +
      "#theia-demo-modal .theia-demo-container {" +
        "width: 100%; max-width: 900px; height: 85vh; max-height: 720px;" +
        "background: #0f172a;" +
        "border: 1px solid rgba(212, 175, 55, 0.4);" +
        "border-radius: 18px;" +
        "box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6);" +
        "display: flex; flex-direction: column;" +
        "overflow: hidden;" +
      "}" +
      "#theia-demo-modal .theia-demo-header {" +
        "padding: 0.9rem 1.25rem;" +
        "background: #1e293b;" +
        "border-bottom: 1px solid rgba(255, 255, 255, 0.1);" +
        "display: flex; align-items: center; justify-content: space-between;" +
      "}" +
      "#theia-demo-modal iframe {" +
        "width: 100%; height: 100%; border: none; background: #ffffff;" +
      "}" +
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
