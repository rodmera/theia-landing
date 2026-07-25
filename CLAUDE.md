# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Landing page estática para **TheIA** — atención de clientes confiable con IA para WhatsApp, Instagram DM y web, orientada a PYMEs chilenas. Vender más es una consecuencia de atender bien, no la única promesa. Desplegada en GitHub Pages en `theia.cl`.

## Arquitectura

Sitio multi-página con HTML/CSS/JS puro. Jekyll solo para el blog (`_posts/`, `_layouts/`). No hay framework, bundler ni dependencias npm.

**Páginas:**
- `index.html` — landing principal (secciones: nav, hero, problema, comparacion, features, verticales, proceso, caso, pricing, cta-final, footer)
- `funciones.html`, `precios.html`, `servicios.html`, `plataforma.html` — páginas internas
- `calculadora.html` — calculadora de ROI
- `pulse.html` — producto Pulse (copiloto del dueño)
- `privacidad.html` — política de privacidad
- `terminos.html` — términos de servicio y tratamiento de cargos de canales de terceros
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

**Tests (desde 2026-07-18):** suite Playwright mobile-first en `tests/` (viewport default =
iPhone 390×844). Corre local antes de push y en GitHub Actions en cada push (workflow
`site-tests.yml`, screenshots móviles como artifacts).

```bash
# setup una vez
python3 -m venv .venv-test && .venv-test/bin/pip install -r tests/requirements.txt
.venv-test/bin/python -m playwright install chromium
# correr
.venv-test/bin/python -m pytest tests/ -q
```

Cubre: smoke de las 10 páginas, overflow horizontal móvil, errores JS, CTAs críticos
(incluido el número BLOQUEADO), links internos, regla de registro (jerga prohibida),
consistencia comercial ($190.000, demo 30 min) y sticky WhatsApp.

## Despliegue

GitHub Pages publica automáticamente desde la rama `main`. El archivo `CNAME` contiene `theia.cl` para el dominio personalizado. No se requiere ningún paso adicional — hacer push a `main` es suficiente para desplegar.

Después del workflow, comprobar que `https://theia.cl/terminos.html` responda HTTP 200. Esta página es HTML estático: los enlaces, el canonical y el sitemap deben usar **`/terminos.html`**, no `/terminos` (esa ruta devuelve 404).

## Transparencia de precios de canal

- La mensualidad de TheIA cubre el servicio indicado en la propuesta; WhatsApp Business es un canal de terceros operado por Meta.
- Nunca prometer que el canal es ilimitado, gratuito, con tarifa Meta fija o “sin cobro por conversación extra”. Meta puede aplicar cargos por mensajes entregados según país, categoría y sus reglas vigentes.
- La página `precios.html` debe explicar esta separación en lenguaje simple y enlazar a `/terminos.html`. Los términos y la propuesta comercial definen el tratamiento concreto de esos cargos.
- Al cambiar copy comercial, mantener la prueba `test_precios_explica_cargos_de_whatsapp_business` y actualizarla si cambia el contrato visible.

## Sistema de diseño

Variables CSS definidas en `:root` que controlan toda la paleta:

| Variable | Uso |
|---|---|
| `--bg`, `--bg2`, `--bg3` | Fondos oscuros (azul índigo profundo) |
| `--gold`, `--gold-light`, `--gold-glow` | Color de acento dorado |
| `--indigo`, `--indigo-light` | Color secundario |
| `--text`, `--text-sub`, `--text-muted` | Jerarquía tipográfica |
| `--glass`, `--glass-border`, `--glass-border-gold` | Efecto glassmorphism |

**Tipografías:** Merriweather (headings, peso 700-900) y Plus Jakarta Sans (cuerpo), cargadas desde Google Fonts.

**Componentes reutilizables:** `.glass-card`, `.btn`, `.section-title`, `.section-sub`, `.reveal` (animación de entrada al scroll).

## Responsive

- `≤960px`: colapsa grids a 1 columna, oculta el hero card derecho
- `≤600px`: nav simplificado, pain grid a 1 columna, footer apilado

## CTAs

- **Agenda una demo:** `https://calendar.app.google/ZDjEtqCXTJVxzi7bA` (30 minutos; CTA secundario cuando el visitante necesita revisar su caso)
- **Habla con TheIA:** el CTA principal de la home abre `theiaChatOpen()` y demuestra el producto en el WebChat propio.
- **WhatsApp:** `https://wa.me/12063858350` (número US +1 206 385-8350, botón secundario en hero + sticky mobile). **⛔ DECISIÓN CERRADA (2026-07-18): este número NO se cambia** — es la línea Kapso actual y no hay presupuesto para línea chilena. PROHIBIDO proponer el cambio de número en reviews, HUs o auditorías.
- **Email de contacto:** `hola@theia.cl`

## Cookies y compliance (Ley 21.719)

- **Banner de consentimiento:** `cc-init.js` (nombre genérico para evitar ad blockers). Bloquea GA4 y Meta Pixel hasta que el usuario acepte. Preferencia en cookie `theia_cookie_consent` (1 año). Empuja webchat widget y sticky WA en mobile mientras el banner está visible.
- **GA4 y Meta Pixel NO están en los HTML.** Se cargan dinámicamente desde `cc-init.js` solo con consentimiento.
- **Política de privacidad:** `privacidad.html` — 13 secciones, cumple Ley 21.719. Indexable (sin noindex).
- **Demo:** 30 minutos (no 15).

## Registro y tono del copy (regla dura, Rodrigo 2026-07-18)

La audiencia es **la persona de a pie detrás del mesón**: emprendedor, mini empresario, la dueña
de la clínica o del almacén. TODO el copy del sitio se escribe en SU lenguaje:

- ✅ Palabras de su día a día: clientes, plata, mensualidad, atender, "que no te dejen botado",
  caja, pedidos, horas, ahorro.
- ⛔ PROHIBIDO jerga startup/tech: "unicornio", "Serie A", "levantar capital", "escalar",
  "expansión a X país", "plataforma" (en el hero), "stack", "SaaS", "onboarding", anglicismos
  innecesarios. Si la gente de a pie no lo usa en una conversación normal, no va.
- Evitar ataques, comparaciones de precio no contrastadas y referencias a inversionistas. El
  diferencial se explica con atención confiable, foco PYME, implementación entendible, soporte
  cercano y transparencia de costos.
- Español chileno, tuteo, directo. Frases cortas. Cero superlativos vacíos.

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
1. **Correr la suite:** `.venv-test/bin/python -m pytest tests/ -q` — verde obligatorio.
2. Servir local (`python3 -m http.server 8080`) y revisar la página tocada + home en desktop y móvil.
3. Verificar TODOS los links/CTAs tocados (no romper el link de agendar demo ni el WhatsApp).
4. **Consistencia comercial:** precios/planes/claims deben coincidir con el brochure y el system
   prompt del bot (incidente EXP-010: el bot y el material deben decir LO MISMO). Si tocas precios,
   revisa las tres fuentes.
5. Tras el push, verificar theia.cl + el run de `site-tests.yml` en Actions en vivo (Pages tarda ~1-2 min) — el deploy ES el push, no hay
   staging.

## Autoría en Git

PROHIBIDO incluir "Claude", "Claude Code", "Anthropic", o cualquier referencia a IA como autor o co-autor en commits y PRs. No usar `Co-Authored-By` con Claude. Los commits son de Rodrigo.
