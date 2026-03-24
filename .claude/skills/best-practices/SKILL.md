---
name: best-practices
description: Apply modern web development best practices for security, compatibility, and code quality. Use when asked to "apply best practices", "security audit", "modernize code", "code quality review", or "check for vulnerabilities".
license: MIT
metadata:
  author: web-quality-skills
  version: "1.0"
---
# Best practices
Modern web development standards based on Lighthouse best practices audits. Covers security, browser compatibility, and code quality patterns.
## Security
### HTTPS everywhere
**Enforce HTTPS:**
```html
<!-- Bad: Mixed content -->
<img src="http://example.com/image.jpg">
<script src="http://cdn.example.com/script.js"></script>
<!-- Good: HTTPS only -->
<img src="https://example.com/image.jpg">
<script src="https://cdn.example.com/script.js"></script>
```
### Content Security Policy (CSP)
```html
<!-- Basic CSP via meta tag -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' https://trusted-cdn.com;
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;
               connect-src 'self' https://api.example.com;">
```
### Input sanitization
```javascript
// Bad: XSS vulnerable
element.innerHTML = userInput;
document.write(userInput);
// Good: Safe text content
element.textContent = userInput;
```
---
## Browser compatibility
### Doctype declaration
```html
<!-- Good: HTML5 doctype -->
<!DOCTYPE html>
<html lang="en">
```
### Character encoding
```html
<!-- Good: Charset as first element in head -->
<html>
<head>
  <meta charset="UTF-8">
  <title>Page</title>
</head>
```
### Viewport meta tag
```html
<!-- Good: Responsive viewport -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page</title>
</head>
```
### Feature detection
```javascript
// Bad: Browser detection (brittle)
if (navigator.userAgent.includes('Chrome')) { }
// Good: Feature detection
if ('IntersectionObserver' in window) { }
// Good: Using @supports in CSS
@supports (display: grid) {
  .container { display: grid; }
}
```
---
## Deprecated APIs
### Avoid these
```javascript
// Bad: document.write (blocks parsing)
document.write('<script src="..."><\/script>');
// Good: Dynamic script loading
const script = document.createElement('script');
script.src = '...';
document.head.appendChild(script);
```
### Event listener passive
```javascript
// Bad: Non-passive touch/wheel (may block scrolling)
element.addEventListener('touchstart', handler);
// Good: Passive listeners (allows smooth scrolling)
element.addEventListener('touchstart', handler, { passive: true });
```
---
## Code quality
### Valid HTML
```html
<!-- Bad: Invalid HTML -->
<div id="header">
<div id="header"> <!-- Duplicate ID -->
<a href="/"><button>Click</button></a> <!-- Invalid nesting -->
<!-- Good: Valid HTML -->
<header id="site-header"></header>
<a href="/" class="button">Click</a>
```
### Semantic HTML
```html
<!-- Bad: Non-semantic -->
<div class="header">
  <div class="nav">
    <div class="nav-item">Home</div>
  </div>
</div>
<!-- Good: Semantic HTML5 -->
<header>
  <nav>
    <a href="/">Home</a>
  </nav>
</header>
<main>
  <article>
    <h1>Headline</h1>
  </article>
</main>
```
### Image aspect ratios
```html
<!-- Bad: Distorted images -->
<img src="photo.jpg" width="300" height="100">
<!-- Good: CSS object-fit for flexibility -->
<img src="photo.jpg" style="width: 300px; height: 200px; object-fit: cover;">
```
---
## Performance best practices
### Avoid blocking patterns
```html
<!-- Bad: Blocking script -->
<script src="heavy-library.js"></script>
<!-- Good: Deferred script -->
<script defer src="heavy-library.js"></script>
<!-- Bad: Blocking CSS import -->
@import url('other-styles.css');
<!-- Good: Link tags (parallel loading) -->
<link rel="stylesheet" href="styles.css">
```
### Efficient event handlers
```javascript
// Bad: Handler on every element
items.forEach(item => {
  item.addEventListener('click', handleClick);
});
// Good: Event delegation
container.addEventListener('click', (e) => {
  if (e.target.matches('.item')) {
    handleClick(e);
  }
});
```
### Memory management
```javascript
// Good: Using AbortController
const controller = new AbortController();
window.addEventListener('resize', handler, { signal: controller.signal });
// Cleanup:
controller.abort();
```
---
## Audit checklist
### Security (critical)
- [ ] HTTPS enabled, no mixed content
- [ ] CSP headers configured
- [ ] Security headers present
- [ ] No exposed source maps
### Compatibility
- [ ] Valid HTML5 doctype
- [ ] Charset declared first in head
- [ ] Viewport meta tag present
- [ ] No deprecated APIs used
- [ ] Passive event listeners for scroll/touch
### Code quality
- [ ] No console errors
- [ ] Valid HTML (no duplicate IDs)
- [ ] Semantic HTML elements used
- [ ] Proper error handling
### UX
- [ ] No intrusive interstitials
- [ ] Permission requests in context
- [ ] Clear error messages
- [ ] Appropriate image aspect ratios
## Tools
| Tool | Purpose |
|------|---------|
| [SecurityHeaders.com](https://securityheaders.com) | Header analysis |
| [W3C Validator](https://validator.w3.org) | HTML validation |
| Lighthouse | Best practices audit |
| [Observatory](https://observatory.mozilla.org) | Security scan |
