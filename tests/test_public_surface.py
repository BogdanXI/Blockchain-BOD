from pathlib import Path

from scripts.validate_public_surface import find_violations


def test_ordinary_project_documentation_is_allowed(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "The project documents its architecture, tooling and development process.",
        encoding="utf-8",
    )
    assert find_violations(tmp_path, ["README.md"]) == []


def test_private_workspace_paths_are_rejected(tmp_path: Path) -> None:
    private_dir = tmp_path / ".agents"
    private_dir.mkdir()
    (private_dir / "notes.md").write_text("internal notes", encoding="utf-8")

    violations = find_violations(tmp_path, [".agents/notes.md"])
    assert violations == ["private path: .agents/notes.md"]


def test_high_confidence_credentials_are_rejected(tmp_path: Path) -> None:
    token = "gh" + "p_" + ("A" * 36)
    private_key_header = "-----BEGIN " + "PRIVATE KEY" + "-----"
    (tmp_path / "sample.txt").write_text(
        f"token={token}\n{private_key_header}", encoding="utf-8"
    )

    violations = find_violations(tmp_path, ["sample.txt"])
    assert violations == ["possible credential material: sample.txt"]
