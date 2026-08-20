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

**Tests (desde 2026-07-18; optimizado 2026-08-15):** suite Playwright mobile-first en
`tests/` (viewport default = iPhone 390×844). Corre local antes de push y en GitHub
Actions en cada push (workflow `site-tests.yml`, screenshots móviles como artifacts).

```bash
# setup una vez
python3 -m venv .venv-test && .venv-test/bin/pip install -r tests/requirements.txt
.venv-test/bin/python -m playwright install chromium
# correr (paralelo: -n 4, ~47s; antes >5 min)
.venv-test/bin/python -m pytest tests/ -q -n 4
# serial (diagnóstico, ~2.5 min)
.venv-test/bin/python -m pytest tests/ -q
```

Optimización 2026-08-15: fixtures `mobile_page`/`desktop_page` son session-scope (un
contexto para toda la suite, no uno por test), waits de navegación reducidos
(150-200ms) y la suite corre en paralelo con `pytest-xdist -n 4` (igual que el CI).
Las esperas de 600ms en `test_design_contract.py`/`test_crm_page_content.py` son
intencionales (verifican animaciones) y NO deben reducirse.

Cubre: smoke de las 10 páginas, overflow horizontal móvil, errores JS, CTAs críticos
(incluido el número BLOQUEADO), links internos, regla de registro (jerga prohibida),
consistencia comercial ($250.000, demo 30 min) y sticky WhatsApp.

### Estándar Canónico de Tarjetas / Cards (Regla Dura, 2026-08-19)

**PROHIBIDO** inventar estilos inline, alinear íconos a la izquierda o pegar los apoyos visuales a los títulos. Toda tarjeta (`.theia-card`) en las 26 páginas del sitio DEBE gobernarse exclusivamente por `site-cards.css` respetando la estructura semántica canónica:

```html
<div class="theia-card">
  <div class="theia-card__visual">
    <div class="piece-icon-wrap">
      <!-- SVG width="24" height="24" stroke="var(--gold-light)" -->
    </div>
  </div>
  <div class="theia-card__content">
    <h3>Título de la Tarjeta</h3>
    <p>Descripción clara y concisa...</p>
  </div>
</div>
```

**Reglas de Maquetación de Cards:**
1. **Apoyo Visual Centrado:** `.theia-card__visual` SIEMPRE está centrado horizontalmente (`align-self: center`, `justify-content: center`) con exactamente `margin-bottom: 1.25rem` (20px) de separación con el título. Jamás pegado al texto.
2. **Dimensiones del Badge:** `.piece-icon-wrap` mide `52px × 52px`, `border-radius: 12px`, fondo `rgba(212, 175, 55, 0.08)` y borde `1px solid var(--glass-border-gold)`.
3. **Contenido Centrado:** `.theia-card__content` tiene título `h3` (`Merriweather`, 1.15rem, margin-bottom: 0.65rem) y descripción `p` (`Plus Jakarta Sans`, 0.9rem, line-height: 1.65, color `var(--text-sub)`), ambos rigurosamente centrados (`text-align: center`).
4. **Contenedor:** `.theia-card` tiene `padding: 2.25rem 1.75rem`, `border-radius: 18px`, fondo `var(--glass)`, borde `1px solid var(--glass-border)` y hover con glow dorado (`transform: translateY(-4px)`).

### Estándar de QA de Interacción Frontend (Regla Dura, 2026-08-19)

- **Prohibido validar menús/dropdowns flotantes con `.hover()` instantáneo:** Playwright teletransporta el puntero en 0ms y enmascara gaps físicos entre el trigger y el popover.
- **Simulación continua obligatoria:** Todo menú desplegable o popover debe validarse simulando el trayecto del mouse con `page.mouse.move()` en pasos interpolados desde el botón hasta la tarjeta interior, verificando que no ocurra `mouseleave` prematuro.
- **Doble gatillo mandatorio (Hover + Click Pinning):** Los dropdowns deben soportar apertura por hover con puente continuo sin gaps (padding/margin estructural) Y persistencia con clic (estado pinned) para accesibilidad y usabilidad táctil.

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

**Design System oficial (desde 2026-08-12):** documento canónico consolidado del ecosistema en `~/Vaults/Digital-Brain/04-Procesos/Plantillas/202608121018 - Design System TheIA — documento oficial consolidado del ecosistema.md` — cubre landing, blog, webchat, posts y panel admin. Especificación detallada del landing (fuente de verdad local): `~/Vaults/Digital-Brain/04-Procesos/Plantillas/Plantilla_LookFeel_theia-landing.md`.

**Tipografías (fuente de verdad en `~/Vaults/Digital-Brain/04-Procesos/Plantillas/Plantilla_LookFeel_theia-landing.md`):**

- **Merriweather** (headings) — pesos disponibles: **700, 900**
- **Plus Jakarta Sans** (cuerpo) — pesos disponibles: **400, 500, 700**

**⛔ REGLA DURA — Tipografías:**
- NO cargar otras familias de Google Fonts (no Inter, no Roboto, no Montserrat, no Poppins, etc.).
- NO usar pesos que no estén en la lista (Merriweather 800, Plus Jakarta 600 — el navegador hace fallback y se rompe la consistencia visual).
- Pesos canónicos: **Merriweather 900** para H1/H2 principales; **700** para H3/sub-headings. **Plus Jakarta 700** para botones/UI importante; **500** para cuerpo destacado; **400** para texto normal.

**⛔ REGLA DURA — Iconos de canales:**
- NO usar emojis genéricos (💬, 📷, 🌐) para representar canales oficiales en paneles visuales.
- SÍ usar SVGs inline con los logos oficiales y colores de marca: WhatsApp `#25D366`, Instagram `#E1306C`, Web `#6366F1`.

**⛔ REGLA DURA — Vistas:**
- El panel del hero y similares NO debe mostrar **sesiones de chat simuladas** (burbujas user/bot estilo chatbot). Eso refuerza la idea de TheIA como "solo un chatbot" y contradice el discurso paraguas.
- Patrón vigente: **Vista 360 del cliente** (avatar con iniciales, nombre, estado, canales con conteo, contexto de la última conversación).

**⛔ REGLA DURA — Widgets Flotantes y Frame del WebChat:**
- En desktop (`min-width: 769px`), existe **un único widget flotante de atención** en la esquina inferior derecha: el asistente WebChat propio de TheIA (`#theia-widget-btn`). No duplicar ni amontonar botones flotantes en desktop (estilo Dapta.ai; WhatsApp va como barra en móvil y en CTAs orgánicos en desktop).
- El botón del WebChat usa gradiente dorado de marca, ícono SVG vectorial AI Spark (no emojis 💬) y tooltip flotante *"Probar conversación en vivo ✨"*.
- El frame desplegado (`#theia-widget-box`) usa header azul índigo `#0f172a` con borde dorado `#d4af37` e ícono SVG.
- Las respuestas rápidas (`.theia-quick-replies button`) usan fondo oscuro `#0f172a` con texto blanco `#ffffff` de alto contraste. PROHIBIDO usar texto dorado claro sobre fondo blanco (bajo contraste ilegible).

**Componentes reutilizables:** `.glass-card`, `.btn-gold`, `.btn-ghost`, `.btn-whatsapp`, `.section-title`, `.section-sub`, `.reveal` (animación de entrada al scroll).

## Responsive

- `≤960px`: colapsa grids a 1 columna, oculta el hero card derecho
- `≤600px`: nav simplificado, pain grid a 1 columna, footer apilado

## CTAs

- **Agenda una demo:** `https://calendar.app.google/ZDjEtqCXTJVxzi7bA` (30 minutos; CTA secundario cuando el visitante necesita revisar su caso)
- **Habla con TheIA:** el CTA principal de la home abre `theiaChatOpen()` y demuestra el producto en el WebChat propio.
- **Atribución del CTA:** siempre llamar al helper compartido `openTheiaChat('<source-estable>')`. El widget valida y envía esa fuente al backend; este guarda el primer origen del contacto sin sobrescribir una campaña existente. Usar identificadores breves en minúsculas y guiones (ejemplo: `atencion-whatsapp`), nunca copy visible ni PII.
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
- **Toda HU que toque front debe cumplir el Design System oficial** (`04-Procesos/Plantillas/202608121018 - Design System TheIA — documento oficial consolidado del ecosistema`): tipografías, paleta, iconos SVG, patrón de vista 360 y rutas de assets. El gate incluye `tests/test_design_contract.py`.
- Cerrar una HU: mismo protocolo del vault (`estado: implementado` + `commit:` SOLO tras el deploy
  verificado en theia.cl).

### 🔒 Al pasar a prod, el vault se actualiza en la MISMA sesión (obligatorio)

El vault es la fuente de verdad del estado **real y priorizado** de TheIA. Si el frontmatter miente,
Rodrigo decide sobre datos falsos. En la nota de la HU, apenas theia.cl sirva el cambio:

1. `estado: implementado` + `commit: <hash>`.
2. **El hash se obtiene con `git rev-parse --short HEAD` (o `git log`) y se verifica con
   `git show --stat <hash>` ANTES de escribirlo.** Prohibido escribirlo de memoria o inventarlo.
3. **Si no lo sabes, `commit: ""`.** Vacío es honesto; inventado es falsificar la trazabilidad.
4. **Prohibidos los placeholders** (`docus`, `d0XX_algo`, "pendiente"): es un hash real o está vacío.
5. Reemplazar el tag de estado (`- backlog` → `- implementado`) y el `topic`.
6. Aclaraciones SOLO en `observaciones:`, nunca dentro de `estado:`.
7. Cerrar corriendo `python3 ~/.openclaw/workspace/tools/theia-hu-health/check.py` → **13/13 verde**.

**Antes de cambiar cualquier `estado`:** leer la nota **completa** (la sección
`## Decisión de portafolio` va al FINAL del cuerpo) y correr `git grep <HU-ID>`. Si el ID ya está
citado en el código, la HU está implementada y **no puede volver** a un estado activo.

> Por qué es regla y no sugerencia: la auditoría del 2026-07-27 encontró **51 HU con `commit:` que
> mentía** — 29 hashes de 40 caracteres que no existen en ningún repo del disco (uno repetido en 6
> notas) y 22 literales tipo `docus`. Los checks 12 y 13 del validador ahora bloquean ambas cosas.

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

## 🔒 Prevención de colisiones entre agentes

Tres agentes de coding pueden editar este repo (Claude, Pi, Codex). Para evitar pisarse:
- **Siempre usar el lock antes de empezar a trabajar:**
  ```python
  from lock_agent import repo_lock, LockHeld
  with repo_lock("REPO_PATH") as info:
      # trabajar aquí
  ```
- Si ves `LockHeld`, otro agente ya está trabajando: aborta o coordiná con él.
