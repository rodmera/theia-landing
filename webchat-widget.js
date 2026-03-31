/**
 * TheIA Web Chat Widget — Track C: US-200 AC3
 * Uso: <script src="/.../webchat-widget.js"
 *            data-api-key="TU_API_KEY"
 *            data-api-url="https://tu-app.herokuapp.com"
 *            data-title="Asistente Virtual"
 *            data-color="#6366f1">
 *      </script>
 */
(function () {
  "use strict";

  const script = document.currentScript;
  const API_KEY = script.getAttribute("data-api-key") || "";
  const API_URL = (script.getAttribute("data-api-url") || "").replace(/\/$/, "");
  const TITLE = script.getAttribute("data-title") || "Chat";
  const COLOR = script.getAttribute("data-color") || "#6366f1";
  const WELCOME_MSG = script.getAttribute("data-welcome") || "¡Hola! 👋 ¿En qué puedo ayudarte hoy?";
  const STORAGE_KEY = "theia_session_" + API_KEY.slice(0, 8);
  const HISTORY_KEY = "theia_history_" + API_KEY.slice(0, 8);
  const COOKIE_KEY  = "theia_vid_"     + API_KEY.slice(0, 8); // cookie 180 días (cubre incógnito y caché limpio)
  const PRECHAT = script.getAttribute("data-prechat") !== "false"; // default: true

  if (!API_KEY || !API_URL) {
    console.warn("[TheIA Widget] data-api-key y data-api-url son requeridos.");
    return;
  }

  /* ── Estilos ── */
  const style = document.createElement("style");
  style.textContent = `
    #theia-widget-btn {
      position: fixed; bottom: 24px; right: 24px; z-index: 9998;
      width: 56px; height: 56px; border-radius: 50%; border: none; cursor: pointer;
      background: ${COLOR}; color: #fff; font-size: 26px;
      box-shadow: 0 4px 16px rgba(0,0,0,.25);
      display: flex; align-items: center; justify-content: center;
      transition: transform .2s;
    }
    #theia-widget-btn:hover { transform: scale(1.08); }
    #theia-widget-btn .theia-badge {
      position: absolute; top: -4px; right: -4px;
      background: #ef4444; color: #fff;
      border-radius: 50%; width: 18px; height: 18px;
      font-size: 11px; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
    }
    #theia-widget-box {
      position: fixed; bottom: 90px; right: 24px; z-index: 9999;
      width: 340px; max-height: 520px;
      border-radius: 16px; overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,.22);
      display: flex; flex-direction: column;
      background: #fff; font-family: system-ui, sans-serif;
      transform: scale(0.85) translateY(20px);
      transform-origin: bottom right;
      opacity: 0; pointer-events: none;
      transition: opacity .2s, transform .2s;
    }
    #theia-widget-box.theia-open {
      opacity: 1; pointer-events: auto;
      transform: scale(1) translateY(0);
    }
    #theia-widget-header {
      padding: 14px 16px;
      background: ${COLOR};
      color: #fff;
      font-weight: 700; font-size: 15px;
      display: flex; align-items: center; justify-content: space-between;
    }
    #theia-widget-header button {
      background: none; border: none; color: #fff;
      font-size: 20px; cursor: pointer; line-height: 1;
      padding: 0 4px;
    }
    #theia-widget-messages {
      flex: 1; overflow-y: auto; padding: 16px 12px;
      display: flex; flex-direction: column; gap: 8px;
      background: #f9fafb;
    }
    .theia-msg {
      max-width: 82%;
      padding: 9px 13px;
      border-radius: 14px;
      font-size: 14px; line-height: 1.45;
      word-break: break-word;
    }
    .theia-msg.bot {
      align-self: flex-start;
      background: #fff;
      border: 1px solid #e5e7eb;
      color: #1f2937;
    }
    .theia-msg.user {
      align-self: flex-end;
      background: ${COLOR};
      color: #fff;
    }
    .theia-msg img {
      max-width: 100%; border-radius: 8px; margin-top: 6px; display: block;
    }
    .theia-typing {
      align-self: flex-start;
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      padding: 10px 16px;
      font-size: 20px; letter-spacing: 2px;
      color: #9ca3af;
    }
    #theia-widget-input {
      display: flex; gap: 8px; padding: 12px;
      border-top: 1px solid #e5e7eb; background: #fff;
    }
    #theia-widget-input input {
      flex: 1; border: 1px solid #d1d5db; border-radius: 22px;
      padding: 8px 14px; font-size: 14px; outline: none;
      transition: border-color .15s;
    }
    #theia-widget-input input:focus { border-color: ${COLOR}; }
    #theia-widget-input button {
      border: none; border-radius: 50%;
      width: 38px; height: 38px; cursor: pointer;
      background: ${COLOR}; color: #fff;
      font-size: 16px; display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; transition: opacity .15s;
    }
    #theia-widget-input button:disabled { opacity: .5; cursor: not-allowed; }
    #theia-prechat {
      padding: 20px 16px; display: flex; flex-direction: column; gap: 12px;
      background: #f9fafb; flex: 1; justify-content: center;
    }
    #theia-prechat p { margin: 0; font-size: 14px; color: #374151; text-align: center; }
    #theia-prechat input {
      border: 1px solid #d1d5db; border-radius: 8px; padding: 10px 12px;
      font-size: 14px; outline: none; width: 100%; box-sizing: border-box;
    }
    #theia-prechat input:focus { border-color: ${COLOR}; }
    #theia-prechat button {
      background: ${COLOR}; color: #fff; border: none; border-radius: 8px;
      padding: 10px; font-size: 14px; font-weight: 600; cursor: pointer;
      transition: opacity .15s;
    }
    #theia-prechat button:hover { opacity: .9; }
    #theia-powered {
      text-align: center; padding: 6px; font-size: 11px; color: #9ca3af;
      border-top: 1px solid #f3f4f6; background: #fff;
    }
    #theia-powered a { color: #6366f1; text-decoration: none; font-weight: 600; }
    #theia-powered a:hover { text-decoration: underline; }
    @media (max-width: 400px) {
      #theia-widget-box { width: calc(100vw - 24px); right: 12px; }
    }
  `;
  document.head.appendChild(style);

  /* ── Cookie helpers (dual-storage: localStorage + cookie 180d) ── */
  function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + "=" + encodeURIComponent(value) + "; expires=" + expires + "; path=/; SameSite=Lax; Secure";
  }
  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(?:^|; )" + name.replace(/[\\^$.*+?()[\]{}|]/g, "\\$&") + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : null;
  }
  function persistToken(token) {
    try { localStorage.setItem(STORAGE_KEY, token); } catch (e) {}
    setCookie(COOKIE_KEY, token, 180);
  }

  /* ── Estado ── */
  let sessionToken = null;
  try { sessionToken = localStorage.getItem(STORAGE_KEY); } catch (e) {}
  if (!sessionToken) sessionToken = getCookie(COOKIE_KEY); // fallback: incógnito o caché limpio
  let isOpen = false;
  let pendingBadge = 0;
  let prechatDone = false;
  try { prechatDone = !!localStorage.getItem(HISTORY_KEY); } catch (e) {}

  /* ── Sound notification (programmatic beep) ── */
  function _playNotif() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = 800;
      gain.gain.value = 0.08;
      osc.start();
      osc.stop(ctx.currentTime + 0.12);
    } catch (e) {}
  }

  /* ── HTML ── */
  const btn = document.createElement("button");
  btn.id = "theia-widget-btn";
  btn.innerHTML = "💬";
  btn.setAttribute("aria-label", "Abrir chat");

  const box = document.createElement("div");
  box.id = "theia-widget-box";
  box.innerHTML = `
    <div id="theia-widget-header">
      <span>💬 ${TITLE}</span>
      <button id="theia-close-btn" aria-label="Cerrar">&times;</button>
    </div>
    <div id="theia-prechat" style="display:none;">
      <p><strong>👋 Antes de empezar</strong></p>
      <input type="text" id="theia-prechat-name" placeholder="Tu nombre" autocomplete="given-name" />
      <input type="email" id="theia-prechat-email" placeholder="Tu email (opcional)" autocomplete="email" />
      <button id="theia-prechat-btn">Iniciar conversación</button>
    </div>
    <div id="theia-widget-messages"></div>
    <div id="theia-widget-input">
      <input type="text" id="theia-msg-input" placeholder="Escribe tu mensaje..." autocomplete="off" />
      <button id="theia-send-btn" aria-label="Enviar">&#9658;</button>
    </div>
    <div id="theia-powered">Potenciado por <a href="https://theia.cl" target="_blank" rel="noopener">TheIA</a></div>
  `;

  document.body.appendChild(btn);
  document.body.appendChild(box);

  const messages = document.getElementById("theia-widget-messages");
  const input = document.getElementById("theia-msg-input");
  const sendBtn = document.getElementById("theia-send-btn");

  /* ── Persistencia: guardar/restaurar historial ── */
  function _saveHistory() {
    try {
      const msgs = [];
      messages.querySelectorAll(".theia-msg").forEach(el => {
        msgs.push({ role: el.classList.contains("user") ? "user" : "bot", html: el.innerHTML });
      });
      sessionStorage.setItem(HISTORY_KEY, JSON.stringify(msgs));
    } catch (e) {}
  }
  function _restoreHistory() {
    try {
      const raw = sessionStorage.getItem(HISTORY_KEY);
      if (!raw) return false;
      const msgs = JSON.parse(raw);
      if (!msgs.length) return false;
      msgs.forEach(m => {
        const div = document.createElement("div");
        div.className = "theia-msg " + m.role;
        div.innerHTML = m.html;
        messages.appendChild(div);
      });
      scrollBottom();
      return true;
    } catch (e) { return false; }
  }

  /* ── Pre-chat form ── */
  const prechatEl = document.getElementById("theia-prechat");
  const chatMessages = document.getElementById("theia-widget-messages");
  const chatInput = document.getElementById("theia-widget-input");

  function _showPrechat() {
    prechatEl.style.display = "flex";
    chatMessages.style.display = "none";
    chatInput.style.display = "none";
    document.getElementById("theia-prechat-name").focus();
  }
  function _hidePrechat() {
    prechatEl.style.display = "none";
    chatMessages.style.display = "flex";
    chatInput.style.display = "flex";
  }

  /* ── Helpers ── */
  function toggleChat() {
    isOpen = !isOpen;
    box.classList.toggle("theia-open", isOpen);
    btn.setAttribute("aria-expanded", isOpen);
    if (isOpen) {
      pendingBadge = 0;
      updateBadge();
      // Si hay historial previo, restaurar
      if (messages.children.length === 0) {
        const restored = _restoreHistory();
        if (restored) {
          _hidePrechat();
          prechatDone = true;
        } else if (PRECHAT && !prechatDone) {
          _showPrechat();
          return;
        } else {
          addBotMessage(WELCOME_MSG);
        }
      }
      input.focus();
    }
  }

  function updateBadge() {
    let badge = btn.querySelector(".theia-badge");
    if (pendingBadge > 0) {
      if (!badge) {
        badge = document.createElement("span");
        badge.className = "theia-badge";
        btn.appendChild(badge);
      }
      badge.textContent = pendingBadge;
    } else if (badge) {
      badge.remove();
    }
  }

  function scrollBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  function formatBotText(text) {
    // Escapar HTML para prevenir XSS
    const escaped = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
    // Convertir *negrita* → <strong> (formato WhatsApp/IA)
    const withBold = escaped.replace(/\*([^*\n]+)\*/g, "<strong>$1</strong>");
    // Convertir saltos de línea → <br>
    return withBold.replace(/\n/g, "<br>");
  }

  function addBotMessage(text, mediaUrl) {
    const div = document.createElement("div");
    div.className = "theia-msg bot";
    div.innerHTML = formatBotText(text);
    if (mediaUrl) {
      const ext = mediaUrl.split("?")[0].split(".").pop().toLowerCase();
      const isImage = ["jpg", "jpeg", "png", "gif", "webp"].includes(ext);
      if (isImage) {
        const img = document.createElement("img");
        img.src = mediaUrl;
        img.alt = "";
        div.appendChild(img);
      } else {
        const link = document.createElement("a");
        link.href = mediaUrl;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "📎 Descargar documento";
        link.style.cssText = "display:block;margin-top:6px;color:#6366f1;font-size:0.85rem;";
        div.appendChild(link);
      }
    }
    messages.appendChild(div);
    scrollBottom();
    _saveHistory();
    if (!isOpen) {
      pendingBadge++;
      updateBadge();
      _playNotif();
    }
  }

  function addUserMessage(text) {
    const div = document.createElement("div");
    div.className = "theia-msg user";
    div.textContent = text;
    messages.appendChild(div);
    scrollBottom();
    _saveHistory();
  }

  function showTyping() {
    const div = document.createElement("div");
    div.className = "theia-typing";
    div.id = "theia-typing";
    div.textContent = "···";
    messages.appendChild(div);
    scrollBottom();
    return div;
  }

  function removeTyping() {
    const el = document.getElementById("theia-typing");
    if (el) el.remove();
  }

  /* ── Enviar mensaje (con throttle anti-spam) ── */
  let _lastSendTime = 0;
  async function sendMessage() {
    const now = Date.now();
    if (now - _lastSendTime < 2000) return; // Throttle: 1 msg cada 2 segundos
    _lastSendTime = now;

    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    sendBtn.disabled = true;
    addUserMessage(text);
    const typingEl = showTyping();

    try {
      const res = await fetch(API_URL + "/api/chat/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-Key": API_KEY,
        },
        body: JSON.stringify({ message: text, session_token: sessionToken }),
      });

      const data = await res.json();
      removeTyping();

      if (data.session_token) {
        sessionToken = data.session_token;
        persistToken(sessionToken);
      }

      if (data.reply) {
        addBotMessage(data.reply, data.media_url || null);
      }
    } catch (err) {
      removeTyping();
      addBotMessage("Error de conexión. Por favor intenta de nuevo.");
      console.error("[TheIA Widget]", err);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  /* ── Eventos ── */
  btn.addEventListener("click", toggleChat);
  document.getElementById("theia-close-btn").addEventListener("click", toggleChat);
  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  /* ── Pre-chat form submit ── */
  document.getElementById("theia-prechat-btn").addEventListener("click", function () {
    const name = document.getElementById("theia-prechat-name").value.trim();
    if (!name) {
      document.getElementById("theia-prechat-name").style.borderColor = "#ef4444";
      return;
    }
    const email = document.getElementById("theia-prechat-email").value.trim();
    prechatDone = true;
    _hidePrechat();

    // Enviar datos como primer mensaje (la IA los capturará con update_contact_info)
    const intro = email ? `Hola, soy ${name}. Mi email es ${email}` : `Hola, soy ${name}`;
    addBotMessage(WELCOME_MSG);
    // Simular envío del mensaje con los datos del pre-chat
    input.value = intro;
    sendMessage();
  });
  document.getElementById("theia-prechat-name").addEventListener("keydown", function (e) {
    if (e.key === "Enter") document.getElementById("theia-prechat-btn").click();
  });
  document.getElementById("theia-prechat-email").addEventListener("keydown", function (e) {
    if (e.key === "Enter") document.getElementById("theia-prechat-btn").click();
  });
})();
