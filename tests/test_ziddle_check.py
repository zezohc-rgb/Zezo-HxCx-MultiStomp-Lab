"""Tests for the external Ziddle diagnostic bridge (no emulator required)."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from multistomp_lab.ziddle_check import check_zdl


class ZiddleCheckTests(unittest.TestCase):
    def test_valid_command_invocation(self):
        with tempfile.TemporaryDirectory() as folder:
            zdl = Path(folder) / "effect.ZDL"
            emulator = Path(folder) / "matcheck.exe"
            zdl.write_bytes(b"fixture")
            emulator.write_bytes(b"fixture")
            with patch("multistomp_lab.ziddle_check.subprocess.run") as run:
                check_zdl(str(zdl), matcheck=str(emulator), knobs=2, bypass=1)
                args, kwargs = run.call_args
                self.assertEqual(args[0], [
                    str(emulator.resolve()), "--params", "2",
                    "--bypass", "1", str(zdl.resolve())
                ])
                self.assertFalse(kwargs["check"])
                self.assertTrue(kwargs["capture_output"])

    def test_rejects_missing_emulator(self):
        with tempfile.TemporaryDirectory() as folder:
            zdl = Path(folder) / "effect.zdl"
            zdl.write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "matcheck"):
                check_zdl(str(zdl), matcheck=str(Path(folder) / "missing"), knobs=2)

    def test_rejects_invalid_knobs(self):
        with self.assertRaises(ValueError):
            check_zdl("not-present.zdl", matcheck="missing", knobs=99)

    def test_rejects_non_zdl(self):
        with tempfile.TemporaryDirectory() as folder:
            zdl = Path(folder) / "effect.txt"
            zdl.write_bytes(b"fixture")
            with self.assertRaises(ValueError):
                check_zdl(str(zdl), matcheck="missing", knobs=2)


if __name__ == "__main__":
    unittest.main()
