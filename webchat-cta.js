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
