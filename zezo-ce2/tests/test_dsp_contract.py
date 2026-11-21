"""Static contract checks: host tests must reflect the actual C DSP constants.

These tests do not execute TI C6000 code and do not establish hardware safety.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DSP = (ROOT / "src" / "zezo_ce2" / "zezo_ce2.c").read_text()
SMOKE = (ROOT / "tests" / "test_signal_smoke.py").read_text()
MATH = (ROOT / "tests" / "test_chorus_math.py").read_text()


class DSPContractTests(unittest.TestCase):
    def test_audio_block_and_state_capacity(self):
        self.assertRegex(DSP, r"#define\s+N\s+1024u")
        self.assertRegex(DSP, r"#define\s+CLEAR_STEP\s+128u")
        self.assertRegex(DSP, r"for\s*\(int i=0;i<8;i\+\+\)")
        self.assertIn("sizeof(State)+N*sizeof(float)+8u", DSP)
        self.assertIn("if(!s->ready)", DSP)

    def test_rate_lfo_matches_host_smoke(self):
        self.assertIn("(0.30f+3.20f*rate)*0.000022675737f", DSP)
        self.assertIn("(.30+3.20*rate)*.000022675737", SMOKE)
        self.assertIn("(.30 + 3.20 * rate) * .000022675737", MATH)

    def test_delay_modulation_matches_host_smoke(self):
        self.assertIn("0.21794872f*depth*tri", DSP)
        self.assertIn(".21794872*depth*tri", SMOKE)
        self.assertIn("0.21794872 * depth * tri", MATH)
        self.assertIn("171.99f*inv", DSP)
        self.assertIn("171.99*(1+m+m*m+m*m*m+m*m*m*m)", SMOKE)
        self.assertIn("171.99 * inv", MATH)
        self.assertIn("if(!(d>=128.0f))d=128.0f;if(d>256.0f)d=256.0f", DSP)

    def test_controls_and_stereo_output_contract(self):
        self.assertIn("norm(params[5])", DSP)
        self.assertIn("norm(params[6])", DSP)
        self.assertIn("buf[i]=1.115f*(0.65f*l+0.35f*wet)", DSP)
        self.assertIn("buf[i+8]=1.115f*(0.65f*r+0.35f*wet)", DSP)
        # The CE-2-style mono wet signal is now fed by both inputs; dry L/R
        # paths remain separate. This is not independent stereo chorus DSP.
        self.assertIn("input=0.5f*(l+r)", DSP)


if __name__ == "__main__":
    unittest.main()
