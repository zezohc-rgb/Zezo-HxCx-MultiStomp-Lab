"""Host-side algebraic tests for CE-2 mono-wet / stereo-dry routing.

These are routing contract checks, not TI emulation or physical pedal tests.
"""
from pathlib import Path
import unittest

DSP = (Path(__file__).resolve().parents[1] / "src" / "zezo_ce2" / "zezo_ce2.c").read_text()


def fold_to_mono(left, right):
    return 0.5 * (left + right)


def output(left, right, wet):
    return (1.115 * (0.65 * left + 0.35 * wet),
            1.115 * (0.65 * right + 0.35 * wet))


class StereoRoutingTests(unittest.TestCase):
    def test_code_uses_both_inputs_for_wet(self):
        self.assertIn("input=0.5f*(l+r)", DSP)
        self.assertIn("buf[i]=1.115f*(0.65f*l+0.35f*wet)", DSP)
        self.assertIn("buf[i+8]=1.115f*(0.65f*r+0.35f*wet)", DSP)

    def test_right_only_signal_reaches_mono_wet_input(self):
        self.assertEqual(fold_to_mono(0.0, 0.4), 0.2)
        self.assertEqual(fold_to_mono(0.4, 0.0), 0.2)

    def test_swapping_inputs_swaps_dry_outputs(self):
        a = output(0.4, -0.2, 0.1)
        b = output(-0.2, 0.4, 0.1)
        self.assertAlmostEqual(a[0], b[1])
        self.assertAlmostEqual(a[1], b[0])

    def test_opposite_phase_inputs_cancel_in_mono_wet(self):
        # Known limitation of a mono fold-down, not a true stereo chorus.
        self.assertAlmostEqual(fold_to_mono(0.4, -0.4), 0.0)


if __name__ == "__main__":
    unittest.main()
