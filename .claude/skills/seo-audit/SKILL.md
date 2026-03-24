---
name: seo-audit
description: Auditoría SEO técnica de todas las páginas del sitio. Revisa meta tags, headings, structured data, OG tags, canonical URLs y performance hints.
---

# Auditoría SEO técnica

Revisa TODOS los archivos HTML del proyecto para validar SEO técnico.

## Checklist por página

### Meta tags obligatorios
- [ ] `<title>` presente, <= 60 caracteres, incluye keyword + marca
- [ ] `<meta name="description">` presente, <= 160 caracteres, incluye CTA
- [ ] `<link rel="canonical">` apuntando a URL correcta
- [ ] `<meta name="robots">` (si aplica — noindex para privacidad)
- [ ] `<meta name="author">` presente
- [ ] `<meta name="geo.region" content="CL">`
- [ ] `<meta name="geo.placename" content="Santiago, Chile">`

### Open Graph (compartir en redes)
- [ ] `og:type` (website o article)
- [ ] `og:url` (URL canónica)
- [ ] `og:title` (<= 60 chars)
- [ ] `og:description` (<= 160 chars)
- [ ] `og:image` (URL absoluta a logo o imagen)
- [ ] `og:locale` (es_CL)
- [ ] `og:site_name` (TheIA)

### Twitter Card
- [ ] `twitter:card` (summary o summary_large_image)
- [ ] `twitter:title`
- [ ] `twitter:description`
- [ ] `twitter:image`

### Structured Data (JSON-LD)
- [ ] Schema.org SoftwareApplication o Organization presente en homepage
- [ ] BlogPosting schema en posts del blog
- [ ] Datos coherentes con el contenido visible

### Headings
- [ ] Exactamente 1 `<h1>` por página
- [ ] Jerarquía correcta (h1 > h2 > h3, sin saltos)
- [ ] Keywords relevantes en h1 y h2

### Imágenes
- [ ] Todas las `<img>` tienen `alt` descriptivo
- [ ] Atributos `width` y `height` presentes (evitar CLS)
- [ ] `loading="lazy"` en imágenes below-the-fold

### Performance hints
- [ ] Google Fonts con `preconnect`
- [ ] Scripts con `async` o `defer` donde sea posible
- [ ] No hay CSS/JS render-blocking innecesario

### Analytics
- [ ] GA4 tag presente en TODAS las páginas
- [ ] Meta Pixel presente en TODAS las páginas
- [ ] CSP permite los dominios de analytics

## Archivos a revisar
Todos los `.html` en raíz, `blog/index.html`, `_layouts/post.html`

## Formato del reporte
Tabla por página con estado (OK / FALTA / ERROR) para cada item.

## Acción
Reportar primero, luego corregir los items marcados como FALTA o ERROR.
