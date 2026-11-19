"""Contrato del pre-chat del WebChat en la home: nombre y correo obligatorios (decisión del 2026-11-08, commit b5f8ec6).

Antes esta regla la comprobaba r2sport-whatsapp-bot leyendo este archivo por ruta absoluta; vive aquí, junto al HTML que gobierna.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def test_home_activa_el_prechat_obligatorio():
    assert 'data-prechat="true"' in (RAIZ / "index.html").read_text(encoding="utf-8")
