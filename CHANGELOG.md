# Changelog - TheIA Landing Page

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [1.3.0] - 2026-03-19

### Añadido

- **Bubble proactivo en webchat**: Tooltip animado que aparece a los 15s en desktop invitando al visitante a chatear. Máximo 3 apariciones por usuario (localStorage). No se muestra en mobile.

## [1.2.0] - 2026-03-17

### Añadido

- **Carousel de integraciones**: 12 logos de tecnologías (Python, Claude, FastAPI, PostgreSQL, etc.) con scroll infinito y pausa al hover.
- **Trust strip Google for Startups**: Mención "Participante del programa Google for Startups Cloud" con líneas divisorias estilo Kapso debajo del hero.
- **Screenshots en Dashboard**: Imágenes reales de inbox y dashboard con efecto zoom al hover.
- **Alianza PLAI**: Card en Servicios Extra con ícono, descripción y links a plai.cl e Instagram.
- **Blog Jekyll**: 3 artículos SEO con layout dedicado, links en nav y footer.
- **Pulse, QR Check-In, NPS, documentos y memoria cross-canal**: Nuevas features en landing.

### Cambiado

- **Tipografía premium**: Hero h1 aumentado a `clamp(2.6rem, 5vw, 4.2rem)`, títulos de sección a `clamp(2rem, 3.5vw, 3rem)`.
- **Spacing de secciones**: Padding aumentado de 5.5rem a 6.5rem.
- **CTA WhatsApp**: Actualizado a número WhatsApp Business TheIA.

### Corregido

- **Webchat widget**: Path corregido de absoluto a relativo para compatibilidad con file://.
- **Privacidad**: Padding-top consistente con nav de 100px.

## [1.1.0] - 2026-02-21

### Añadido

- **Botón "Scroll to Top"**: Añadida funcionalidad de scroll suave hacia arriba con efecto glassmorphism.
- **Sección Agent API**: Nueva tarjeta de característica destacando la integración con n8n y OpenClaw.
- **Sección Chat Aislado**: Nueva tarjeta para explicar el modo de pruebas de la base de conocimiento.
- **Iconografía Profesional**: Migración total de emojis a iconos SVG minimalistas (estilo Lucide) en todas las secciones (Hero, Problema, Funciones, Verticales, Agenda, Dashboard, Proceso).

### Cambiado

- **Identidad Visual "Premium"**:
  - Cambiado color de fondo de Púrpura a **Slate Oscuro** (`#0f172a`).
  - Actualizados acentos de Indigo estándar a **Flat Indigo** (`#4f46e5`).
  - Cambiado Dorado estándar a **Champagne Gold** (`#d4af37`).
- **Branding de Integraciones**: Implementados logos oficiales de **n8n** y **OpenClaw** con estilo unificado.
- **WhatsApp CTAs**: Reemplazados emojis `💬` por iconos oficiales de WhatsApp SVG en todos los botones de acción.
- **Refinamiento de Estilos**: Reducción de opacidad en el canvas de fondo y suavizado de sombras en tarjetas de cristal.

### Corregido

- **Navegación**: Corregidos los enlaces de los logos en el Header y Footer que apuntaban a `/` (causando errores locales) para que ahora funcionen como anclas `#` al inicio de la página.
