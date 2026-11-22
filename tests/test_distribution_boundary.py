from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_distribution_allowlist_excludes_historical_token_economics_modules() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    modules = set(project["tool"]["setuptools"]["py-modules"])

    active_modules = {
        "bod_cli",
        "bod_evidence_envelope",
        "bod_portable",
        "bod_evidence_formats",
        "bod_anchor",
        "bod_verify_simple",
    }
    historical_modules = {
        "bod_protocol",
        "bod_economy",
        "bod_economic_operations",
        "bod_simulation",
        "bod_continuity",
        "bod_project_state",
        "bod_repository_adapter",
        "bod_verification",
    }

    assert active_modules <= modules
    assert not modules.intersection(historical_modules)
    assert project["project"]["scripts"]["bod"] == "bod_cli:main"
