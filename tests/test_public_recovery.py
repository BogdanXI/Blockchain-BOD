import subprocess
import sys


def test_public_recovery_experiment():
    result = subprocess.run(
        [sys.executable, "experiments/run_public_recovery.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
