/**
 * site-nav.js — Comportamiento accesible para el navbar TheIA (TASK-202608191930)
 */
(function () {
  function initSiteNav() {
    // 1. Gestión del Dropdown de Soluciones en Desktop
    const solutions = document.querySelectorAll('.site-nav__solutions');
    solutions.forEach((container) => {
      const trigger = container.querySelector('.site-nav__solutions-trigger');
      const popover = container.querySelector('.site-nav__popover');
      if (!trigger || !popover) return;

      function openMenu() {
        if (window.innerWidth > 960) {
          container.classList.add('is-open');
          trigger.setAttribute('aria-expanded', 'true');
        }
      }

      function closeMenu() {
        if (window.innerWidth > 960) {
          container.classList.remove('is-open');
          trigger.setAttribute('aria-expanded', 'false');
        }
      }

      // Hover
      container.addEventListener('mouseenter', openMenu);
      container.addEventListener('mouseleave', closeMenu);

      // Clic en trigger
      trigger.addEventListener('click', (e) => {
        if (window.innerWidth > 960) {
          e.stopPropagation();
          const isOpen = trigger.getAttribute('aria-expanded') === 'true';
          if (isOpen) {
            closeMenu();
          } else {
            openMenu();
          }
        }
      });
    });

    // Cerrar dropdown al hacer clic fuera o con Escape
    document.addEventListener('click', (e) => {
      if (window.innerWidth > 960) {
        solutions.forEach((container) => {
          if (!container.contains(e.target)) {
            container.classList.remove('is-open');
            const trigger = container.querySelector('.site-nav__solutions-trigger');
            if (trigger) trigger.setAttribute('aria-expanded', 'false');
          }
        });
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && window.innerWidth > 960) {
        solutions.forEach((container) => {
          container.classList.remove('is-open');
          const trigger = container.querySelector('.site-nav__solutions-trigger');
          if (trigger) {
            trigger.setAttribute('aria-expanded', 'false');
            trigger.focus();
          }
        });
      }
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth <= 960) {
        solutions.forEach((container) => {
          container.classList.remove('is-open');
          const trigger = container.querySelector('.site-nav__solutions-trigger');
          if (trigger) trigger.setAttribute('aria-expanded', 'false');
        });
      } else {
        const navCta = document.querySelector('.nav-cta');
        if (navCta) {
          navCta.classList.remove('active');
          document.body.classList.remove('mobile-menu-open');
        }
      }
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
