/**
 * site-nav.js — Comportamiento accesible y mejoras interactivas para el navbar TheIA (TASK-202608191916)
 */
(function () {
  function initSiteNav() {
    // 1. Gestión accesible del menú de Soluciones en Desktop
    const disclosures = document.querySelectorAll('.site-nav__solutions-disclosure');
    disclosures.forEach((d) => {
      // Hover interactivo para apertura de details en desktop
      d.addEventListener('mouseenter', () => {
        if (window.innerWidth > 960) {
          d.setAttribute('open', '');
        }
      });

      d.addEventListener('mouseleave', () => {
        if (window.innerWidth > 960) {
          d.removeAttribute('open');
        }
      });
    });

    if (disclosures.length) {
      document.addEventListener('click', (e) => {
        if (window.innerWidth > 960) {
          disclosures.forEach((d) => {
            if (d.open && !d.contains(e.target)) {
              d.removeAttribute('open');
            }
          });
        }
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && window.innerWidth > 960) {
          disclosures.forEach((d) => {
            if (d.open) {
              d.removeAttribute('open');
              const summary = d.querySelector('summary');
              if (summary) summary.focus();
            }
          });
        }
      });

      window.addEventListener('resize', () => {
        if (window.innerWidth <= 960) {
          disclosures.forEach((d) => d.removeAttribute('open'));
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSiteNav);
  } else {
    initSiteNav();
  }
})();
