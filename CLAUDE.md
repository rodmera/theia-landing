# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Landing page estática para **TheIA** — agente de ventas IA para WhatsApp, Instagram DM y web, orientado al mercado chileno y latinoamericano. Desplegada en GitHub Pages en `theia.cl`.

## Arquitectura

Sitio multi-página con HTML/CSS/JS puro. Jekyll solo para el blog (`_posts/`, `_layouts/`). No hay framework, bundler ni dependencias npm.

**Páginas:**
- `index.html` — landing principal (secciones: nav, hero, problema, comparacion, features, verticales, proceso, caso, pricing, cta-final, footer)
- `funciones.html`, `precios.html`, `servicios.html`, `plataforma.html` — páginas internas
- `calculadora.html` — calculadora de ROI
- `pulse.html` — producto Pulse (copiloto del dueño)
- `privacidad.html` — política de privacidad
- `blog/` — posts Jekyll (`_posts/`)
- `webchat-widget.js` — widget de chat web embebido, se conecta al backend TheIA vía API

**Estructura de index.html:**
- `<style>` — todos los estilos en línea, usando CSS custom properties para el sistema de diseño
- `<body>` — secciones semánticas
- `<script>` — canvas animado de red neuronal + IntersectionObserver para animaciones de scroll

## Desarrollo local

Abrir directamente en el navegador:
```bash
open index.html
```

O servir con cualquier servidor estático para evitar restricciones de CORS:
```bash
python3 -m http.server 8080
# luego visitar http://localhost:8080
```

No hay linter, tests ni build configurados.

## Despliegue

GitHub Pages publica automáticamente desde la rama `main`. El archivo `CNAME` contiene `theia.cl` para el dominio personalizado. No se requiere ningún paso adicional — hacer push a `main` es suficiente para desplegar.

## Sistema de diseño

Variables CSS definidas en `:root` que controlan toda la paleta:

| Variable | Uso |
|---|---|
| `--bg`, `--bg2`, `--bg3` | Fondos oscuros (azul índigo profundo) |
| `--gold`, `--gold-light`, `--gold-glow` | Color de acento dorado |
| `--indigo`, `--indigo-light` | Color secundario |
| `--text`, `--text-sub`, `--text-muted` | Jerarquía tipográfica |
| `--glass`, `--glass-border`, `--glass-border-gold` | Efecto glassmorphism |

**Tipografías:** Montserrat (headings, peso 700-900) y Open Sans (cuerpo), cargadas desde Google Fonts.

**Componentes reutilizables:** `.glass-card`, `.btn`, `.section-title`, `.section-sub`, `.reveal` (animación de entrada al scroll).

## Responsive

- `≤960px`: colapsa grids a 1 columna, oculta el hero card derecho
- `≤600px`: nav simplificado, pain grid a 1 columna, footer apilado

## CTAs

- **Agendar Demo:** `https://calendar.app.google/ZDjEtqCXTJVxzi7bA` (CTA principal en nav, hero y footer)
- **WhatsApp:** `https://wa.me/12063858350` (número US +1 206 385-8350, botón secundario en hero + sticky mobile)
- **Email de contacto:** `hola@theia.cl`

## Cookies y compliance (Ley 21.719)

- **Banner de consentimiento:** `cc-init.js` (nombre genérico para evitar ad blockers). Bloquea GA4 y Meta Pixel hasta que el usuario acepte. Preferencia en cookie `theia_cookie_consent` (1 año). Empuja webchat widget y sticky WA en mobile mientras el banner está visible.
- **GA4 y Meta Pixel NO están en los HTML.** Se cargan dinámicamente desde `cc-init.js` solo con consentimiento.
- **Política de privacidad:** `privacidad.html` — 13 secciones, cumple Ley 21.719. Indexable (sin noindex).
- **Demo:** 30 minutos (no 15).

## Backlog (desde 2026-07-18)

Las HUs del sitio viven en el **mismo backlog del vault que TheIA producto** (notas `HU-WEB-*` en
`00-Inbox/UniqueNotes/`), con **épica `web`** y campo **`repo: theia-landing`** en el frontmatter.
Consultar: `python3 ~/projects/r2sport-whatsapp-bot/scripts/backlog.py --epica web`.
- Los agentes que trabajen ACÁ solo toman HUs con `repo: theia-landing`. Las demás son del producto
  (r2sport-whatsapp-bot, otros gates) — no tomarlas desde este repo.
- Cerrar una HU: mismo protocolo del vault (`estado: implementado` + `commit:` SOLO tras el deploy
  verificado en theia.cl).

## Gate de este repo (no hay pytest — el gate es otro)

Antes de commitear a `main` (main = deploy directo a theia.cl vía Pages):
1. Servir local (`python3 -m http.server 8080`) y revisar la página tocada + home en desktop y móvil.
2. Verificar TODOS los links/CTAs tocados (no romper el link de agendar demo ni el WhatsApp).
3. **Consistencia comercial:** precios/planes/claims deben coincidir con el brochure y el system
   prompt del bot (incidente EXP-010: el bot y el material deben decir LO MISMO). Si tocas precios,
   revisa las tres fuentes.
4. Tras el push, verificar theia.cl en vivo (Pages tarda ~1-2 min) — el deploy ES el push, no hay
   staging.

## Autoría en Git

PROHIBIDO incluir "Claude", "Claude Code", "Anthropic", o cualquier referencia a IA como autor o co-autor en commits y PRs. No usar `Co-Authored-By` con Claude. Los commits son de Rodrigo.
