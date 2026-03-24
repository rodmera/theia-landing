---
name: core-web-vitals
description: Optimize Core Web Vitals (LCP, INP, CLS) for better page experience and search ranking. Use when asked to "improve Core Web Vitals", "fix LCP", "reduce CLS", "optimize INP", "page experience optimization", or "fix layout shifts".
license: MIT
metadata:
  author: web-quality-skills
  version: "1.0"
---

# Core Web Vitals optimization

Targeted optimization for the three Core Web Vitals metrics that affect Google Search ranking and user experience.

## The three metrics

| Metric | Measures | Good | Needs work | Poor |
|--------|----------|------|------------|------|
| **LCP** | Loading | <= 2.5s | 2.5s - 4s | > 4s |
| **INP** | Interactivity | <= 200ms | 200ms - 500ms | > 500ms |
| **CLS** | Visual Stability | <= 0.1 | 0.1 - 0.25 | > 0.25 |

Google measures at the **75th percentile** -- 75% of page visits must meet "Good" thresholds.

---

## LCP: Largest Contentful Paint

LCP measures when the largest visible content element renders. Usually this is:
- Hero image or video
- Large text block
- Background image
- `<svg>` element

### Common LCP issues

**1. Slow server response (TTFB > 800ms)**
```
Fix: CDN, caching, optimized backend, edge rendering
```

**2. Render-blocking resources**
```html
<!-- Bad: Blocks rendering -->
<link rel="stylesheet" href="/all-styles.css">

<!-- Good: Critical CSS inlined, rest deferred -->
<style>/* Critical above-fold CSS */</style>
<link rel="preload" href="/styles.css" as="style"
      onload="this.onload=null;this.rel='stylesheet'">
```

**3. Slow resource load times**
```html
<!-- Bad: No hints, discovered late -->
<img src="/hero.jpg" alt="Hero">

<!-- Good: Preloaded with high priority -->
<link rel="preload" href="/hero.webp" as="image" fetchpriority="high">
<img src="/hero.webp" alt="Hero" fetchpriority="high">
```

### LCP optimization checklist

- [ ] TTFB < 800ms (use CDN, edge caching)
- [ ] LCP image preloaded with fetchpriority="high"
- [ ] LCP image optimized (WebP/AVIF, correct size)
- [ ] Critical CSS inlined (< 14KB)
- [ ] No render-blocking JavaScript in <head>
- [ ] Fonts don't block text rendering (font-display: swap)
- [ ] LCP element in initial HTML (not JS-rendered)

---

## INP: Interaction to Next Paint

INP measures responsiveness across ALL interactions (clicks, taps, key presses) during a page visit.

### INP breakdown

Total INP = **Input Delay** + **Processing Time** + **Presentation Delay**

| Phase | Target | Optimization |
|-------|--------|--------------|
| Input Delay | < 50ms | Reduce main thread blocking |
| Processing | < 100ms | Optimize event handlers |
| Presentation | < 50ms | Minimize rendering work |

### Common INP issues

**1. Long tasks blocking main thread**
```javascript
// Bad: Long synchronous task
function processLargeArray(items) {
  items.forEach(item => expensiveOperation(item));
}

// Good: Break into chunks with yielding
async function processLargeArray(items) {
  const CHUNK_SIZE = 100;
  for (let i = 0; i < items.length; i += CHUNK_SIZE) {
    const chunk = items.slice(i, i + CHUNK_SIZE);
    chunk.forEach(item => expensiveOperation(item));
    await new Promise(r => setTimeout(r, 0));
  }
}
```

**2. Heavy event handlers**
```javascript
// Bad: All work in handler
button.addEventListener('click', () => {
  const result = calculateComplexThing();
  updateUI(result);
  trackEvent('click');
});

// Good: Prioritize visual feedback
button.addEventListener('click', () => {
  button.classList.add('loading');
  requestAnimationFrame(() => {
    const result = calculateComplexThing();
    updateUI(result);
  });
  requestIdleCallback(() => trackEvent('click'));
});
```

### INP optimization checklist

- [ ] No tasks > 50ms on main thread
- [ ] Event handlers complete quickly (< 100ms)
- [ ] Visual feedback provided immediately
- [ ] Heavy work deferred with requestIdleCallback
- [ ] Third-party scripts don't block interactions
- [ ] Debounced input handlers where appropriate

---

## CLS: Cumulative Layout Shift

CLS measures unexpected layout shifts. A shift occurs when a visible element changes position between frames without user interaction.

### Common CLS causes

**1. Images without dimensions**
```html
<!-- Bad: Causes layout shift when loaded -->
<img src="photo.jpg" alt="Photo">

<!-- Good: Space reserved -->
<img src="photo.jpg" alt="Photo" width="800" height="600">

<!-- Good: Or use aspect-ratio -->
<img src="photo.jpg" alt="Photo" style="aspect-ratio: 4/3; width: 100%;">
```

**2. Dynamically injected content**
```javascript
// Bad: Inserts content above viewport
notifications.prepend(newNotification);

// Good: Insert below viewport or use transform
newNotification.style.transform = 'translateY(-100%)';
notifications.prepend(newNotification);
requestAnimationFrame(() => {
  newNotification.style.transform = '';
});
```

**3. Web fonts causing FOUT**
```css
/* Good: Optional font (no shift if slow) */
@font-face {
  font-family: 'Custom';
  src: url('custom.woff2') format('woff2');
  font-display: optional;
}

/* Good: Or match fallback metrics */
@font-face {
  font-family: 'Custom';
  src: url('custom.woff2') format('woff2');
  font-display: swap;
  size-adjust: 105%;
  ascent-override: 95%;
  descent-override: 20%;
}
```

**4. Animations triggering layout**
```css
/* Bad: Animates layout properties */
.animate {
  transition: height 0.3s, width 0.3s;
}

/* Good: Use transform instead */
.animate {
  transition: transform 0.3s;
}
.animate.expanded {
  transform: scale(1.2);
}
```

### CLS optimization checklist

- [ ] All images have width/height or aspect-ratio
- [ ] All videos/embeds have reserved space
- [ ] Ads have min-height containers
- [ ] Fonts use font-display: optional or matched metrics
- [ ] Dynamic content inserted below viewport
- [ ] Animations use transform/opacity only
- [ ] No content injected above existing content

---

## Measurement tools

### Lab testing
- **Chrome DevTools** -> Performance panel, Lighthouse
- **WebPageTest** -> Detailed waterfall, filmstrip
- **Lighthouse CLI** -> `npx lighthouse <url>`

### Field data (real users)
- **Chrome User Experience Report (CrUX)** -> BigQuery or API
- **Search Console** -> Core Web Vitals report
- **web-vitals library** -> Send to your analytics

```javascript
import {onLCP, onINP, onCLS} from 'web-vitals';

function sendToAnalytics({name, value, rating}) {
  gtag('event', name, {
    event_category: 'Web Vitals',
    value: Math.round(name === 'CLS' ? value * 1000 : value),
    event_label: rating
  });
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
```
