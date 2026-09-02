"""Pruebas de la landing de solución B2B Orquestación y Arquitectura Multi-Agente (HU-WEB-039 / HU-WEB-040)."""
from pathlib import Path
import re
import pytest

from conftest import BASE

ROOT = Path(__file__).resolve().parent.parent
ORQUESTACION_HTML = ROOT / "orquestacion.html"


def test_orquestacion_html_exists_and_has_valid_metadata():
    assert ORQUESTACION_HTML.is_file(), "orquestacion.html debe existir"
    content = ORQUESTACION_HTML.read_text(encoding="utf-8")

    assert "<title>Arquitectura y Orquestación Multi-Agente Determinista" in content
    assert 'canonical" href="https://theia.cl/orquestacion"' in content
    assert "Closed-World Entailment" in content
    assert "Diamond Pattern" in content or "Diamond Multi-Especialista" in content


def test_orquestacion_contains_4_layers_and_3_services():
    content = ORQUESTACION_HTML.read_text(encoding="utf-8")

    # Closed-Loop Diagram
    assert 'id="loop"' in content
    assert "El Ciclo de Orquestación" in content
    assert "Context Synthesis" in content
    assert "Multimodal Elicitation" in content
    assert "Adaptive Response" in content
    assert "MULTI-TURN LOOP" in content

    # 4 Capas
    assert "Capa 1: Ingress & Pre-Flight Router" in content
    assert "Capa 2: Especialistas Paralelos" in content
    assert "Capa 3: Verification Gate" in content
    assert "Capa 4: Transacciones & Memoria Bi-Temporal" in content

    # 3 Servicios B2B
    assert "TheIA Enterprise Agents" in content
    assert "Arquitectura Multi-Agente" in content
    assert "Auditoría & Evals de Agentes" in content


def test_orquestacion_contains_interactive_evaluator():
    content = ORQUESTACION_HTML.read_text(encoding="utf-8")
    assert 'id="evaluador"' in content
    assert 'id="step-1"' in content
    assert 'id="step-5"' in content
    assert 'id="step-result"' in content
    assert "evalAnswer" in content


def test_orquestacion_conforms_to_design_system():
    content = ORQUESTACION_HTML.read_text(encoding="utf-8")
    # Tipografías canónicas
    assert "Merriweather" in content
    assert "Plus Jakarta Sans" in content
    # Cero brillos
    assert "--gold-glow" not in content or "var(--gold-glow)" not in content
    assert "drop-shadow(" not in content


def test_orquestacion_interactive_evaluator_in_browser(page):
    page.goto(f"{BASE}/orquestacion.html")
    page.wait_for_load_state("networkidle")

    # Debe iniciar en el paso 1
    assert page.is_visible("#step-1")
    assert not page.is_visible("#step-2")

    # Clic en opción A del paso 1 (0 pts)
    page.locator("#step-1 .eval-option").first.click()
    page.wait_for_timeout(200)

    # Ahora debe estar en paso 2
    assert page.is_visible("#step-2")
    page.locator("#step-2 .eval-option").first.click()
    page.wait_for_timeout(200)

    # Paso 3
    assert page.is_visible("#step-3")
    page.locator("#step-3 .eval-option").first.click()
    page.wait_for_timeout(200)

    # Paso 4
    assert page.is_visible("#step-4")
    page.locator("#step-4 .eval-option").first.click()
    page.wait_for_timeout(200)

    # Paso 5
    assert page.is_visible("#step-5")
    page.locator("#step-5 .eval-option").first.click()
    page.wait_for_timeout(300)

    # Debe mostrar resultado de Riesgo Crítico (0 pts)
    assert page.is_visible("#step-result")
    score_text = page.locator("#result-score").inner_text()
    assert "0 / 100" in score_text
    assert "Riesgo Crítico" in page.locator("#result-title").inner_text()
