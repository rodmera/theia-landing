"""Test de integración que ejecuta la suite determinista completa de FrontendUXAuditor en theia-landing."""
import sys
from pathlib import Path


def test_frontend_ux_auditor_zero_errors():
    skill_script_dir = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "frontend-ux-review" / "scripts"
    sys.path.insert(0, str(skill_script_dir))
    from audit_frontend_ux import FrontendUXAuditor

    repo_dir = Path(__file__).resolve().parent.parent
    auditor = FrontendUXAuditor(repo_dir)
    success = auditor.run()

    assert success is True, f"FrontendUXAuditor encontró {len(auditor.errors)} errores: {auditor.errors}"
    assert len(auditor.errors) == 0
