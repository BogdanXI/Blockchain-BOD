"""Check tracked public files for private workspace material and credential leaks."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

_PRIVATE_PATH_NAMES = {
    ".agents",
    ".repo-os",
    ".env",
    ".secrets",
    "agents.md",
    "project_state.md",
    "private.md",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
}

# High-confidence formats only. Avoid broad keyword scans that create false positives.
_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:[A-Z0-9 ]+)?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
)


def tracked_paths(root: Path = ROOT) -> list[str]:
    """Return repository paths tracked by Git, independent of local untracked files."""
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    return [item.decode("utf-8") for item in output.split(b"\0") if item]


def find_violations(root: Path, paths: list[str]) -> list[str]:
    """Find private paths and high-confidence credential patterns in tracked text files."""
    violations: list[str] = []

    for relative in paths:
        path = Path(relative)
        parts = [part.casefold() for part in path.parts]

        if any(
            part in _PRIVATE_PATH_NAMES
            or part.startswith(".env.")
            or part.startswith("credentials.")
            for part in parts
        ):
            violations.append(f"private path: {relative}")
            continue

        candidate = root / path
        try:
            text = candidate.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
            violations.append(f"possible credential material: {relative}")

    return sorted(set(violations))


def main() -> int:
    violations = find_violations(ROOT, tracked_paths(ROOT))
    if violations:
        print("\n".join(violations))
        return 1

    print("public surface validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
