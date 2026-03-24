---
name: accessibility-review
description: Auditoría de accesibilidad WCAG 2.1 AA para todas las páginas del sitio. Revisa semántica HTML, ARIA, contraste, navegación por teclado y mobile.
---

# Auditoría de accesibilidad (WCAG 2.1 AA)

Revisa TODOS los archivos HTML del proyecto para cumplimiento de accesibilidad.

## Checklist

### 1. Semántica HTML
- [ ] Uso de `<nav>`, `<main>`, `<footer>`, `<section>`, `<article>` donde corresponda
- [ ] `<main>` presente en cada página (solo 1)
- [ ] Landmark roles implícitos correctos
- [ ] Listas (`<ul>`, `<ol>`) para contenido de lista (no divs)

### 2. Imágenes
- [ ] Todas las `<img>` tienen `alt` descriptivo y relevante
- [ ] Imágenes decorativas tienen `alt=""`
- [ ] SVG inline tienen `aria-hidden="true"` si son decorativos

### 3. Formularios
- [ ] Todos los `<input>` tienen `<label>` asociado o `aria-label`
- [ ] Campos requeridos marcados con `required` y feedback visual
- [ ] Mensajes de error accesibles
- [ ] Honeypot fields tienen `aria-hidden="true"` y `tabindex="-1"`

### 4. Enlaces y botones
- [ ] Todo `<a>` tiene texto descriptivo (no "click aquí")
- [ ] Links que abren nueva pestaña indican `target="_blank"` con texto o aria-label
- [ ] Botones tienen `aria-label` si solo contienen ícono
- [ ] Touch targets >= 44x44px en mobile

### 5. Color y contraste
- [ ] Texto sobre fondo: ratio >= 4.5:1 (AA normal text)
- [ ] Texto grande (>= 18px bold o >= 24px): ratio >= 3:1
- [ ] Información no transmitida solo por color
- [ ] Revisar especialmente: texto `--text-muted` sobre `--bg` y `--bg2`

### 6. Navegación por teclado
- [ ] Todos los elementos interactivos son focusables
- [ ] Orden de tab lógico
- [ ] Focus visible en todos los elementos interactivos
- [ ] Menú mobile accesible por teclado (Escape para cerrar)
- [ ] Skip navigation link (nice to have)

### 7. ARIA
- [ ] `aria-label` en botones de ícono (hamburger, close, scroll-to-top)
- [ ] `aria-expanded` en toggles (menú mobile, FAQ accordions)
- [ ] `aria-hidden` en contenido decorativo
- [ ] No usar ARIA cuando HTML semántico es suficiente

### 8. Responsive / Mobile
- [ ] `<meta name="viewport">` presente con `width=device-width`
- [ ] Texto legible sin zoom (>= 16px base)
- [ ] No hay scroll horizontal en mobile
- [ ] Elementos interactivos no se superponen

### 9. Idioma
- [ ] `<html lang="es">` presente en todas las páginas
- [ ] Si hay contenido en otro idioma, marcado con `lang="en"` etc.

## Archivos a revisar
Todos los `.html` en raíz, `blog/index.html`, `_layouts/post.html`

## Formato del reporte
Agrupar por severidad:
- **Crítico**: Bloquea acceso para usuarios con discapacidad
- **Mayor**: Dificulta significativamente el uso
- **Menor**: Mejora recomendada

## Acción
Reportar primero, luego corregir items críticos y mayores.
