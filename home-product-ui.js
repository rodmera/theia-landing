/**
 * home-product-ui.js — Interactividad y micro-UIs de Home (HU-WEB-033)
 * Controla:
 * 1. Switch interactivo de reglas de catálogo vs freno de descuentos.
 * 2. Contador demostrativo de Speed-to-Lead (<60s).
 * 3. Enlaces interactivos del diagrama de orquestación omnicanal.
 */

(function () {
  'use strict';

  function initRulesSwitch() {
    const toggles = document.querySelectorAll('[data-rule-toggle]');
    const normalDisplay = document.getElementById('rule-display-normal');
    const discountDisplay = document.getElementById('rule-display-discount');

    if (!toggles.length || !normalDisplay || !discountDisplay) return;

    toggles.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const mode = btn.getAttribute('data-rule-toggle');
        toggles.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        if (mode === 'discount') {
          normalDisplay.style.display = 'none';
          discountDisplay.style.display = 'flex';
        } else {
          normalDisplay.style.display = 'flex';
          discountDisplay.style.display = 'none';
        }
      });
    });
  }

  function initSpeedToLeadTimer() {
    const timerEl = document.getElementById('speed-timer-count');
    if (!timerEl) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      timerEl.textContent = '00:42s';
      return;
    }

    let seconds = 0;
    const target = 42;

    function step() {
      if (seconds < target) {
        seconds += 1;
        const formatted = seconds < 10 ? '0' + seconds : seconds;
        timerEl.textContent = '00:' + formatted + 's';
        setTimeout(step, 40);
      } else {
        // Pausa y reinicio cíclico cada 6 segundos
        setTimeout(function () {
          seconds = 0;
          timerEl.textContent = '00:00s';
          setTimeout(step, 800);
        }, 6000);
      }
    }

    // Iniciar con IntersectionObserver cuando la sección sea visible
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          step();
          observer.disconnect();
        }
      });
    }, { threshold: 0.2 });

    observer.observe(timerEl);
  }

  function initOrchestrationHighlights() {
    const channelNodes = document.querySelectorAll('.home-ui__channel-node');
    const orchestrationContainer = document.querySelector('.home-ui__orchestration');

    if (!channelNodes.length || !orchestrationContainer) return;

    channelNodes.forEach(function (node) {
      const channel = node.getAttribute('data-channel');
      if (!channel) return;

      node.addEventListener('mouseenter', function () {
        const path = orchestrationContainer.querySelector('.home-ui__flow-path--' + channel);
        if (path) {
          path.style.strokeWidth = '3.5';
          path.style.opacity = '1';
        }
      });

      node.addEventListener('mouseleave', function () {
        const path = orchestrationContainer.querySelector('.home-ui__flow-path--' + channel);
        if (path) {
          path.style.strokeWidth = '';
          path.style.opacity = '';
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initRulesSwitch();
      initSpeedToLeadTimer();
      initOrchestrationHighlights();
    });
  } else {
    initRulesSwitch();
    initSpeedToLeadTimer();
    initOrchestrationHighlights();
  }
})();
