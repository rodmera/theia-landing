---
name: spanish-spell-check
description: Revisa ortografía, tildes y gramática en español en todos los archivos HTML y Markdown del sitio. Usar después de crear o modificar contenido en español.
---

# Revisión ortográfica en español

Revisa TODOS los archivos HTML (.html) y Markdown (.md) del proyecto buscando errores de ortografía en español en texto visible al usuario (no en código CSS, JS, URLs ni atributos HTML internos).

## Qué buscar

### 1. Tildes faltantes (lo más común)
Palabras que SIEMPRE llevan tilde en español:
- Terminadas en -ción: integración, suscripción, implementación, información, configuración, automatización, conversación, atención, satisfacción, recepción, navegación
- Terminadas en -sión: inversión, decisión, comprensión
- Esdrújulas: automático/a, métricas, código, único/a, mínimo, página, línea, rápido/a, técnicas, específicamente, catálogo, públicas, diagnóstico
- Verbos: está, compró, envía, preguntó, implementó
- Pronombres/adverbios: tú (pronombre), más, cómo, qué, cuál, cuánto, cuándo, dónde, después, también, así, sí (afirmativo)
- Otras: menú, día/días, español, diseño/diseñado/diseñar, año, dueño, guía

### 2. Signos de interrogación/exclamación
En español las preguntas llevan ¿ al inicio y ? al final. Buscar preguntas que solo tengan ? sin ¿.

### 3. Consistencia de términos
- "TheIA" (no "Theia", "THEIA", "theia")
- "WhatsApp" (no "Whatsapp", "whatsapp")

### 4. Gramática básica
- Concordancia de género: "la agente" vs "el agente"
- "Si" (condicional) vs "Sí" (afirmativo)
- "Esta" (demostrativo) vs "Está" (verbo estar)

## Archivos a revisar
- `*.html` en la raíz del proyecto
- `_posts/*.md`
- `_layouts/*.html`
- `blog/index.html`

## Formato del reporte
Para cada error:
1. Archivo y línea
2. Texto incorrecto
3. Corrección sugerida

## Acción
Después de reportar, corrige TODOS los errores encontrados usando la herramienta Edit.
