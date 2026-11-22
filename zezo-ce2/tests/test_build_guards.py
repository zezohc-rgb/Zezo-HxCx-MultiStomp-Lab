"""Regression tests for safety gates without invoking TI compiler."""
import os
import pathlib
import subprocess
import sys
import unittest

BUILD = pathlib.Path(__file__).resolve().parents[1] / "src" / "zezo_ce2" / "build.py"

class BuildGuardTests(unittest.TestCase):
    def invoke(self, **env_updates):
        env = os.environ.copy()
        env.pop("ZEZO_FXID_REVIEWED", None)
        env.pop("ZEZO_DIAGNOSTIC_BUILD", None)
        env.update(env_updates)
        return subprocess.run([sys.executable, str(BUILD)], capture_output=True, text=True, env=env)

    def test_wrong_review_token_is_rejected(self):
        result = self.invoke(ZEZO_FXID_REVIEWED="405")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independently review FXID", result.stderr + result.stdout)

    def test_no_review_token_is_rejected(self):
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independently review FXID", result.stderr + result.stdout)

if __name__ == "__main__":
    unittest.main()
