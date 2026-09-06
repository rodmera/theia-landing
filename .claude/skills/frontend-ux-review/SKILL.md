---
name: frontend-ux-review
description: Valida contenido, UX, consistencia visual, navegación mobile y buenas prácticas del Design System TheIA en desarrollo frontend. Úsalo ante cualquier cambio visual, maquetación HTML/CSS, revisión de componentes, auditoría de legibilidad, consistencia tipográfica o responsiveness.
---

# Frontend UX & Design System Review

Skill obligatorio para todo desarrollo frontend en TheIA. Asegura que cada pantalla, componente y texto cumpla con el estándar visual, consistencia tipográfica, experiencia de usuario y contratos mecánicos del ecosistema.

## 🎯 Cuándo invocar este Skill

- Al diseñar o maquetar nuevas páginas, vistas o componentes web.
- Al modificar estilos CSS, espaciados, colores o tipografía.
- Al revisar PRs o diffs que toquen la interfaz pública (`theia-landing`, webchat, etc.).
- Ante quejas de inconsistencia visual ("textos de distinto tamaño", "desalineado", "saturado").
- Antes de commitear o desplegar cualquier cambio a producción.

---

## 1. Contenido & Jerarquía Semántica

- **Jerarquía Estricta:**
  - `H1`: Un único H1 por página (título principal en el Hero).
  - `H2`: Todos los títulos de sección principales deben usar la clase canónica `.section-title`.
  - `H3`: Exclusivo para subtítulos de tarjetas, bloques y ejes temáticos.
- **Speed to Concept (< 3 segundos):**
  - El visitante debe entender el valor de la sección de un vistazo.
  - Eliminar párrafos extensos de relleno o palabrería genérica ("IA avanzada", "solución integral líder").
- **Tono Canónico:**
  - Registro chileno profesional y directo ("la persona de a pie detrás del mesón": clientes, plata, pedidos, agendar, responder a tiempo).
  - PROHIBIDA la jerga de startup: "unicornio", "SaaS", "Serie A", "escalar", "stack", etc.
- **Wording & Calidad Editorial (Reglas de Expertos: NN/g, Podmajersky, Richards):**
  - **Cero Pleonasmos y Tautologías:** Prohibido "completamente gratis", "totalmente automático", "reintentar de nuevo", "lapso de tiempo", "resumen breve", "resultado final", "planes a futuro", "solución integral completa", "bucle circular".
  - **Cero Meta-Lenguaje Obvio de UI:** Prohibido "haz clic aquí", "presiona el botón para", "a continuación te mostramos", "en esta sección puedes ver". Los botones deben usar verbos de acción directos.
  - **Tuteo Consistente:** Tuteo chileno estándar ("tu negocio", "atiende", "conversa", "prueba", "configura"). Prohibido mezclar ustedeo ("su negocio", "sus clientes", "su empresa", "usted") o voseo ("tenés", "hacés").
  - **Cero Fluff y Buzzwords Vacías:** Prohibido "de última generación", "de vanguardia", "de clase mundial", "revolucionario", "sin precedentes", "disruptivo", "paradigma", "holístico", "sinergia", "customer-centric", "seamless".
  - **Cero AI Slop y Clichés Sintéticos de LLMs:** Prohibido fórmulas vacías como "al siguiente nivel", "desbloquear/desatar tu potencial", "empoderar", "imagina un mundo donde", "en el mundo vertiginoso de hoy", "el futuro es hoy", "es importante destacar", "vale la pena señalar", "diseñado meticulosamente", "la solución definitiva", "un tapiz de", "un faro de", "potencia al máximo", "transformación digital". Todo copy debe aterrizar en hechos, números y procesos operativos reales.
  - **Anti-Echoing en Párrafos:** Prohibido repetir la misma palabra sustantiva/verbal 3 o más veces dentro de un mismo párrafo o bloque de texto sin justificación estilística.
  - **Cohesión Título ↔ Subtítulo:** El subtítulo (`.section-sub`) no debe ser un eco tautológico que repita las mismas palabras del título; debe aportar contexto explicativo, valor o justificación operativa.
  - **Integridad de Naming de Marcas:** "TheIA" estricto (no "Theia", "TheIa", "THEIA"), "WhatsApp" estricto (no "Whatsapp"), "Instagram", "Google Gemini".
- **Verdad Comercial & Closed-World:**
  - PROHIBIDO el uso de "próximamente", "soon", "avísame" o promesas de módulos en desarrollo. Lo que está en la web debe operar hoy en producción.

---

## 2. Consistencia Visual & Design System TheIA

### Tipografía Canónica (Regla Dura)
- **Merriweather (Serif):**
  - `900` (Black): Exclusivo para H1 y todos los H2 de sección (`.section-title`). PROHIBIDO degradar H2 a 700.
  - `700` (Bold): Exclusivo para H3 y títulos de tarjetas.
- **Plus Jakarta Sans (Sans-serif):**
  - `400` (Regular): Cuerpo de texto y párrafos estándar.
  - `500` (Medium): Párrafos destacados y subtítulos.
  - `700` (Bold): Botones, CTAs y UI destacada.
- **PROHIBIDO:** Cargar Inter, Roboto, Montserrat o cualquier otra familia no declarada.

### Tipografía en Interfaces de Aplicación y Panel Admin (Regla Dura)
- **100% Plus Jakarta Sans en Aplicación/Admin:** En paneles de administración, dashboards SaaS y herramientas operativas (`admin.theia.cl` / `r2sport-whatsapp-bot`), toda la interfaz (encabezados H1-H6, barras de herramientas, saludos de usuario, tablas, botones, formularios y tarjetas) debe usar rigurosamente **Plus Jakarta Sans** (`400`, `500`, `600`, `700`).
- **PROHIBIDO Serif en UI de Aplicación:** Queda estrictamente PROHIBIDO usar `Merriweather` o fuentes serif en toolbars, saludos de usuario (`Hola, ...`), encabezados de vistas administrativas o cards operativas. La tipografía serif `Merriweather` está reservada con exclusividad para titulares editoriales y marketing del sitio público (`theia.cl`).
- **Consistencia Estructural de Encabezados Admin (`page_header`):** Toda plantilla de vista administrativa que extienda `admin/base.html` DEBE implementar obligatoriamente el bloque `{% block page_header %}` con la estructura canónica:
  ```html
  {% block page_header %}
  <div class="d-flex justify-content-between align-items-center flex-grow-1 me-3">
      <div>
          <h5 class="fw-bold mb-1" style="letter-spacing: -0.01em;">[Título de la Vista]</h5>
          <p class="text-secondary mb-0 small">[Descripción o alcance breve]</p>
      </div>
      <div class="d-flex align-items-center gap-2">
          <!-- Acciones o botones principales de la vista -->
      </div>
  </div>
  {% endblock %}
  ```
  Prohibido omitir `page_header` y colocar títulos en el cuerpo del contenido, pues provoca colisión con el saludo por defecto y duplicidad visual en pantalla.

### Títulos y Subtítulos de Sección Homologados en Landing (Regla Dura 2026-09-04)
- **Títulos (`.section-title` / H2):**
  - `font-family: 'Merriweather', serif; font-weight: 900;`
  - `font-size: clamp(2rem, 3.5vw, 3rem);`
  - `line-height: 1.2; letter-spacing: -0.02em; margin-bottom: 0.75rem; text-align: center; color: var(--text, #ffffff);`
  - Spans dorados (`span.gold`, `.gold`): `color: var(--gold);` (`#d4af37`, TheIA Gold). PROHIBIDO usar `#ebca73` en títulos.
- **Subtítulos (`.section-sub`):**
  - `font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; line-height: 1.65; color: var(--text-sub); max-width: 680px; margin: 0 auto 3rem; text-align: center;`
- **PROHIBICIÓN DE OVERRIDES:**
  - PROHIBIDO introducir selectores compuestos en CSS secundarios (`.specialists-header h2`, `.setup-header h2`) que alteren font-size o font-weight.
  - PROHIBIDO usar `style="font-size:..."` o `style="font-weight:..."` inline en encabezados.

### Consistencia de Alineación en Tarjetas (Layout Alignment)
- **Alineación a la Izquierda en Home:** Todas las tarjetas con título y descripción en `index.html` (`.specialist-card`, `.determinista-card`, `.conecta-card`, `.theia-card` en home) deben tener su icono, título y descripción rigurosamente alineados a la izquierda (`text-align: left`).
- **Prohibición de Texto Centrado en Párrafos de Tarjetas:** Centrar párrafos de 3 o más líneas degrada la legibilidad y genera bordes desiguales.

### Cero Canibalización de CTAs y Taxonomía Limpia
- **Sin Botones Duales Redundantes:** En secciones teaser o de catálogo (como `#servicios-especializados`), prohibido agregar botones duales de agendamiento que compitan con el enlace al catálogo principal.
- **Footer Taxonómico:** Las columnas de navegación del footer (`.footer-links-group`) son exclusivas para enlaces a páginas internas del sitio. Prohibido intercalar enlaces de agendamiento (Google Calendar) o botones destacados en las listas de navegación.

### Paleta de Colores
- Fondo dark slate: `#0f172a` (`--bg`), `#1e293b` (`--bg2`), `#334155` (`--bg3`).
- Acento de marca: TheIA Gold (`#d4af37`), oro claro (`#ebca73`).
- **Restricción Dura del Verde:** `#25D366` / `#34c77b` queda ESTRICTAMENTE limitado a:
  1. Icono y botón oficial de WhatsApp (`.btn-whatsapp`).
  2. Micro-punto indicador de estado de 6px (`● "En línea"`).
  - PROHIBIDO verde en títulos, subtítulos, precios, cifras monetarias, cantidades, bordes o badges.
- Badges (`.dash-badge`): Fondo y texto en tonos TheIA Gold. PROHIBIDO usar morado o índigo.

---

## 3. Accesibilidad WCAG AA & Integridad Técnica

- **Imágenes:** Todo elemento `<img>` debe contar con un atributo `alt` descriptivo no vacío.
- **Botones Interactivos:** Todo `<button>` debe declarar explícitamente `type="button"` o `type="submit"`.
- **Formularios:** Todo campo `<input>` debe contar con su correspondiente `<label for="...">` o `aria-label`.
- **Enlaces & Navegación:**
  - PROHIBIDO enlaces vacíos `href="#"` (provocan saltos inesperados y añaden fragmentos espurios a la URL).
  - Todo enlace interno y ancla (`#...`, `/#...`) debe resolver a una página o ID existente en disco.
- **Touch Targets en Mobile:**
  - Todo elemento interactivo debe tener un área táctil mínima de **44 × 44 px** con al menos 8 px de margen.
- **Cero Desbordamiento Horizontal:**
  - Regla mecánica: `document.documentElement.scrollWidth <= document.documentElement.clientWidth` en cualquier resolución móvil (360px a 430px).

---

## 4. Protocolo de Verificación Mecánica (Checklist Obligatorio)

Antes de entregar o desplegar cualquier desarrollo frontend:

1. **Auditoría Estática Automática (11 Módulos - Landing o Admin):**
   ```bash
   # Para el sitio web / landing:
   python3 ~/.claude/skills/frontend-ux-review/scripts/audit_frontend_ux.py --repo ~/projects/theia-landing
   
   # Para el panel de administración (FastAPI/Jinja):
   python3 ~/.claude/skills/frontend-ux-review/scripts/audit_frontend_ux.py --repo ~/projects/r2sport-whatsapp-bot
   ```
   *Ambos deben resultar en 0 errores.*

2. **Suite de Pruebas de Contrato de Diseño:**
   ```bash
   cd ~/projects/theia-landing && pytest tests/test_design_contract.py
   ```
   *Todos los tests deben pasar exitosamente.*

3. **Verificación Visual en Navegador (Desktop y Mobile):**
   - Verificar la página a 1366×768 px y a 390×844 px (iPhone 15).
   - Inspeccionar visualmente que los títulos de todas las secciones computen a `Merriweather 900` sin disparidades al hacer scroll.
