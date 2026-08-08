"""Verifica que cada feature del CRM en crm.html tenga su atributo data-hu-crm correspondiente.
"""
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
CRM_PAGE = ROOT / "crm.html"


def test_crm_features_tienen_data_hu_crm():
    """Cada feature declarada en crm.html lleva un atributo data-hu-crm."""
    source = CRM_PAGE.read_text(encoding="utf-8")
    expected_hu_tags = [
        "HU-CRM-001",  # Negocios / Kanban
        "HU-CRM-006",  # Campos personalizados
        "HU-CRM-008",  # Timeline / Historial
        "HU-CRM-011",  # Cierre ganado / perdido
        "HU-CRM-012",  # Tareas de venta
        "HU-CRM-027",  # Cotizaciones
        "HU-CRM-029",  # Reportes
    ]
    missing = [tag for tag in expected_hu_tags if f'data-hu-crm="{tag}"' not in source]
    assert not missing, f"Faltan atribuciones data-hu-crm en crm.html: {missing}"
