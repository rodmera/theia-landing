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
  - **Anti-Echoing en Párrafos:** Prohibido repetir la misma palabra sustantiva/verbal 3 o más veces dentro de un mismo párrafo o bloque de texto sin justificación estilística.
  - **Cohesión Título ↔ Subtítulo:** El subtítulo (`.section-sub`) no debe ser un eco tautológico que repita las mismas palabras del título; debe aportar contexto explicativo, valor o justificación operativa.
  - **Integridad de Naming de Marcas:** "TheIA" estricto (no "Theia", "TheIa", "THEIA"), "WhatsApp" estricto (no "Whatsapp"), "Instagram", "Google Gemini", "Ley 21.719".
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

### Títulos y Subtítulos de Sección Homologados (Regla Dura 2026-09-04)
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

### Paleta de Colores
- Fondo dark slate: `#0f172a` (`--bg`), `#1e293b` (`--bg2`), `#334155` (`--bg3`).
- Acento de marca: TheIA Gold (`#d4af37`), oro claro (`#ebca73`).
- **Restricción Dura del Verde:** `#25D366` / `#34c77b` queda ESTRICTAMENTE limitado a:
  1. Icono y botón oficial de WhatsApp (`.btn-whatsapp`).
  2. Micro-punto indicador de estado de 6px (`● "En línea"`).
  - PROHIBIDO verde en títulos, subtítulos, precios, cifras monetarias, cantidades, bordes o badges.
- Badges (`.dash-badge`): Fondo y texto en tonos TheIA Gold. PROHIBIDO usar morado o índigo.

---

## 3. Navegación Mobile & Responsive

- **Cero Desbordamiento Horizontal:**
  - Regla mecánica: `document.documentElement.scrollWidth <= document.documentElement.clientWidth` en cualquier resolución móvil (360px a 430px).
- **Touch Targets:**
  - Todo elemento interactivo (botones, enlaces, selectores) debe tener un área táctil mínima de **44 × 44 px** con al menos 8 px de margen de separación.
- **Formularios en iOS Safari:**
  - Los campos `<input>`, `<textarea>` y `<select>` deben tener `font-size: 16px` (o 1rem) para evitar el zoom automático disruptivo en iPhone.
- **Colapso Inteligente de Grids:**
  - Grids de 3 o 4 columnas deben colapsar limpiamente a 1 columna en pantallas `<= 960px` o `<= 600px`.
  - El apoyo visual del Hero debe posicionarse debajo de los CTAs en móvil, nunca comprimido lateralmente.

---

## 4. Filosofía "Menos es Más" (Look & Feel Ejecutivo)

- **Aire y Respiración:**
  - Priorizar márgenes generosos (`padding: 4rem 0` a `6rem 0` entre secciones) en lugar de amontonar micro-tarjetas.
- **Cero Saturación Visual:**
  - Evitar arcoíris cromáticos. Un fondo oscuro técnico con acentos TheIA Gold transmite autoridad y sobriedad ejecutiva.
- **Contraste Accesible (WCAG AA):**
  - Mínimo 4.5:1 para texto normal, 3:1 para texto grande o UI. Prohibido texto dorado claro sobre blanco o gris oscuro sobre fondo negro.
- **Microinteracciones y Feedback:**
  - Transiciones suaves de 150 a 250ms con curvas bezier (`cubic-bezier(0.16, 1, 0.3, 1)`).
  - Estados `:hover` sutiles con realce de borde (`--glass-border-gold`) y elevación máxima de 3px.

---

## 5. Protocolo de Verificación Mecánica (Checklist Obligatorio)

Antes de entregar o desplegar cualquier desarrollo frontend:

1. **Auditoría Estática Automática:**
   ```bash
   python3 ~/.claude/skills/frontend-ux-review/scripts/audit_frontend_ux.py --repo ~/projects/theia-landing
   ```
   *Debe resultar en 0 errores.*

2. **Suite de Pruebas de Contrato de Diseño:**
   ```bash
   cd ~/projects/theia-landing && pytest tests/test_design_contract.py
   ```
   *Todos los tests deben pasar exitosamente.*

3. **Verificación Visual en Navegador (Desktop y Mobile):**
   - Verificar la página a 1366×768 px y a 390×844 px (iPhone 15).
   - Inspeccionar visualmente que los títulos de todas las secciones computen a `Merriweather 900` sin disparidades al hacer scroll.
