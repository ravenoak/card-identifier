import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(
    importlib.util.find_spec("tensorflow") is None,
    reason="TensorFlow not installed",
)
def test_label_image_help_runs():
    script = Path(__file__).resolve().parents[1] / "scripts" / "label_image.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--help",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "image to be classified" in result.stdout
