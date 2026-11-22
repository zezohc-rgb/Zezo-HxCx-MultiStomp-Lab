"""Static checks for the Zoom memory and control ABI."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DSP = (ROOT / "src" / "zezo_ce2" / "zezo_ce2.c").read_text()


class DSPContractTests(unittest.TestCase):
    def test_audio_block_and_state_capacity(self):
        self.assertRegex(DSP, r"#define\s+N\s+1024u")
        self.assertRegex(DSP, r"#define\s+CLEAR_STEP\s+128u")
        self.assertRegex(DSP, r"for\s*\(int i=0;i<8;i\+\+\)")
        self.assertIn("sizeof(State)+N*sizeof(float)+8u", DSP)
        self.assertIn("if(!s->ready)", DSP)

    def test_controls_use_normalized_abi_slots(self):
        self.assertIn("norm(params[5])", DSP)
        self.assertIn("norm(params[6])", DSP)


if __name__ == "__main__":
    unittest.main()
