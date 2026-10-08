"""Validate the public repository for prohibited provenance and private-workspace material."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

# Encoded literals keep the validator itself free of the strings it is designed to reject.
_FORBIDDEN = tuple(
    bytes.fromhex(value).decode("utf-8")
    for value in (
        "43686174475054",
        "4f70656e4149",
        "6172746966696369616c20696e74656c6c6967656e6365",
        "4c4c4d",
        "475054",
    )
)

_PRIVATE_PATH_PARTS = (
    ".agents",
    ".repo-os",
    "AGENTS.md",
    "PROJECT_STATE.md",
    "STATUS.md",
)


def iter_text_files() -> list[Path]:
    """Validate the tracked public surface, not local ignored build/runtime artifacts."""
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT, text=False
    )
    files: list[Path] = []
    for relative in output.decode("utf-8").split("\x00"):
        if not relative:
            continue
        path = ROOT / relative
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files.append(path)
    return files


def main() -> int:
    violations: list[str] = []

    for path in iter_text_files():
        relative = path.relative_to(ROOT).as_posix()
        if any(part in relative.split("/") for part in _PRIVATE_PATH_PARTS):
            violations.append(f"private path: {relative}")
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        folded = text.casefold()
        for token in _FORBIDDEN:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(token.casefold())}(?![A-Za-z0-9])", folded):
                violations.append(f"prohibited provenance term in: {relative}")
                break

    if violations:
        print("\n".join(sorted(set(violations))))
        return 1

    print("public surface validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
