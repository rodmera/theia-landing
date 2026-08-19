/**
 * site-nav.js — Comportamiento accesible y estabilidad hover para el navbar TheIA (TASK-202608191947)
 */
(function () {
  function initSiteNav() {
    // 1. Gestión accesible y control de estado del Dropdown de Soluciones en Desktop
    const solutions = document.querySelectorAll('.site-nav__solutions');
    solutions.forEach((container) => {
      const trigger = container.querySelector('.site-nav__solutions-trigger');
      const popover = container.querySelector('.site-nav__popover');
      if (!trigger || !popover) return;

      let closeTimer = null;
      let pinned = false;
      let suppressFocusOpen = false;

      function openMenu(options) {
        if (suppressFocusOpen) return;
        const pin = options && options.pin;
        if (closeTimer) {
          clearTimeout(closeTimer);
          closeTimer = null;
        }
        if (pin) {
          pinned = true;
        }
        if (window.innerWidth > 960) {
          container.classList.add('is-open');
          trigger.setAttribute('aria-expanded', 'true');
        }
      }

      function scheduleCloseMenu() {
        if (pinned) return;
        if (container.contains(document.activeElement)) return;
        if (closeTimer) {
          clearTimeout(closeTimer);
        }
        closeTimer = setTimeout(() => {
          closeMenu();
        }, 150);
      }

      function closeMenu(options) {
        const returnFocus = options && options.returnFocus;
        if (closeTimer) {
          clearTimeout(closeTimer);
          closeTimer = null;
        }
        pinned = false;
        container.classList.remove('is-open');
        trigger.setAttribute('aria-expanded', 'false');
        if (returnFocus) {
          suppressFocusOpen = true;
          trigger.focus();
          setTimeout(() => {
            suppressFocusOpen = false;
          }, 150);
        }
      }

      // Eventos de puntero sobre el contenedor completo (trigger + padding continuo + popover)
      container.addEventListener('pointerenter', () => {
        if (window.innerWidth > 960) {
          openMenu({ pin: false });
        }
      });

      container.addEventListener('pointerleave', () => {
        if (window.innerWidth > 960) {
          scheduleCloseMenu();
        }
      });

      // Foco accesible por teclado
      container.addEventListener('focusin', () => {
        if (window.innerWidth > 960) {
          openMenu({ pin: false });
        }
      });

      container.addEventListener('focusout', () => {
        if (window.innerWidth > 960) {
          setTimeout(() => {
            if (!container.contains(document.activeElement)) {
              scheduleCloseMenu();
            }
          }, 20);
        }
      });

      // Clic para anclar (pin) o alternar estado
      trigger.addEventListener('click', (e) => {
        if (window.innerWidth > 960) {
          e.stopPropagation();
          const isOpen = container.classList.contains('is-open');
          if (isOpen && pinned) {
            closeMenu();
          } else {
            openMenu({ pin: true });
          }
        }
      });

      // Cerrar si se hace clic fuera del contenedor
      document.addEventListener('click', (e) => {
        if (window.innerWidth > 960) {
          if (!container.contains(e.target)) {
            closeMenu();
          }
        }
      });

      // Cerrar con Escape
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && window.innerWidth > 960) {
          if (container.classList.contains('is-open')) {
            closeMenu({ returnFocus: true });
          }
        }
      });

      // Reset en cambio de tamaño de ventana
      window.addEventListener('resize', () => {
        if (window.innerWidth <= 960) {
          closeMenu();
        }
      });
    });

    // 2. Gestión unificada del menú móvil off-canvas
    const menuToggle = document.querySelector('.menu-toggle');
    const navCta = document.querySelector('.nav-cta');
    const hasInlineScript = Array.from(document.querySelectorAll('script:not([src])')).some(s => s.textContent.includes('menuToggle'));
    if (menuToggle && navCta && !hasInlineScript && !menuToggle.dataset.navBound) {
      menuToggle.dataset.navBound = 'true';
      menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        navCta.classList.toggle('active');
        document.body.classList.toggle('mobile-menu-open');
      });

      const navLinks = navCta.querySelectorAll('a');
      navLinks.forEach((link) => {
        link.addEventListener('click', () => {
          navCta.classList.remove('active');
          document.body.classList.remove('mobile-menu-open');
        });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSiteNav);
  } else {
    initSiteNav();
  }
})();
