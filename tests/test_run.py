"""Smoke test: run.py writes a well-formed metrics report."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RunSmokeTest(unittest.TestCase):
    def test_run_writes_metrics(self) -> None:
        subprocess.run([sys.executable, str(ROOT / "run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
        result = json.loads((ROOT / "reports" / "metrics.json").read_text(encoding="utf-8"))
        self.assertIn("synthetic", result["data_notice"].lower())
        self.assertTrue(result["metrics"])
        self.assertTrue(result["chart"]["series"])
        self.assertGreater(len(result["flow"]), 1)


if __name__ == "__main__":
    unittest.main()
