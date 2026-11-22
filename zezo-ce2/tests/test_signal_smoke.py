"""Run the stage-2 C audio entry point using the host compiler."""

from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class SignalSmokeTests(unittest.TestCase):
    def test_stage_2_audio(self):
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "host_dsp"
            subprocess.run(
                [
                    "cc", "-std=c99", "-O2", "-fno-pie", "-no-pie",
                    "-fsanitize=undefined", "-fno-sanitize-recover=all",
                    "-DZEZO_STAGE=2", "-I", str(HERE.parent / "src" / "zezo_ce2"),
                    str(HERE / "host_dsp.c"), "-lm", "-o", str(executable),
                ],
                check=True,
            )
            subprocess.run([str(executable)], check=True)


if __name__ == "__main__":
    unittest.main()
