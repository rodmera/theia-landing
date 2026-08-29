// HU-WEB-033: Homologación Partner de IA y Consola de Reglas
/**
 * site-nav.js — Módulo profundo de navegación pública TheIA (TASK-202608192246)
 */
(function () {
  function initSiteNav() {
    // 1. Gestión de Dropdowns en Desktop (Soluciones, Industrias, Recursos)
    const groups = document.querySelectorAll('.site-nav__group, .site-nav__solutions');
    groups.forEach((container) => {
      const trigger = container.querySelector('.site-nav__trigger, .site-nav__solutions-trigger');
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
          // Cerrar otros dropdowns hermanos
          groups.forEach((other) => {
            if (other !== container && other.classList.contains('is-open')) {
              other.classList.remove('is-open');
              const otherTrig = other.querySelector('.site-nav__trigger, .site-nav__solutions-trigger');
              if (otherTrig) otherTrig.setAttribute('aria-expanded', 'false');
            }
          });
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

      // Eventos de puntero sobre el grupo
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

      // Clic para anclar (pin) o alternar
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

      // Cerrar si se hace clic fuera
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

    // 2. Gestión unificada del menú móvil off-canvas (HU-WEB-027)
    const menuToggle = document.querySelector('.menu-toggle');
    const navCta = document.querySelector('.nav-cta, .site-nav');
    if (menuToggle && navCta && !menuToggle.dataset.siteNavBound) {
      menuToggle.dataset.siteNavBound = 'true';
      menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = navCta.classList.toggle('active');
        document.body.classList.toggle('mobile-menu-open');
        menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });

      const navLinks = navCta.querySelectorAll('a');
      navLinks.forEach((link) => {
        link.addEventListener('click', () => {
          navCta.classList.remove('active');
          document.body.classList.remove('mobile-menu-open');
          menuToggle.setAttribute('aria-expanded', 'false');
        });
      });

      window.addEventListener('resize', () => {
        if (window.innerWidth > 960 && navCta.classList.contains('active')) {
          navCta.classList.remove('active');
          document.body.classList.remove('mobile-menu-open');
          menuToggle.setAttribute('aria-expanded', 'false');
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
