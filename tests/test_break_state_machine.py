import subprocess
import sys


def test_break_state_machine_smoke():
    result = subprocess.run(
        [sys.executable, "scripts/break_state_machine.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = result.stdout.strip().splitlines()
    assert lines == [
        "PASS candidate-valid",
        "REJECT invalid-signature",
        "REJECT wrong-evidence",
        "REJECT replay",
        "REJECT state-conflict",
        "REJECT policy-violation",
        "REJECT settlement-without-valid-verification",
    ]
