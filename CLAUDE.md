# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Landing page estática para **TheIA** — agente de ventas IA para WhatsApp, orientado al mercado chileno y latinoamericano. Desplegada en GitHub Pages en `theia.cl`.

## Arquitectura

Todo el sitio vive en un único archivo `index.html` con HTML, CSS y JavaScript embebidos. No hay framework, bundler, ni dependencias npm. No se requiere proceso de build.

**Estructura del archivo:**
- `<style>` — todos los estilos en línea, usando CSS custom properties para el sistema de diseño
- `<body>` — secciones semánticas: `nav`, `hero`, `problema`, `comparacion`, `features`, `verticales`, `proceso`, `caso`, `pricing`, `cta-final`, `footer`
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

## Contacto / WhatsApp CTA

Todos los CTAs apuntan a `https://wa.me/56977298344`. El email de contacto es `rodrigo@theia.cl`.
