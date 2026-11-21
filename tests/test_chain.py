import tempfile
import unittest
from pathlib import Path
from multistomp_lab.chain import Chain, Slot, ChainError

class ChainTests(unittest.TestCase):
    def test_six_slots(self):
        self.assertEqual(len(Chain().slots), 6)

    def test_reject_seven_slots(self):
        with self.assertRaises(ChainError):
            Chain(slots=[Slot() for _ in range(7)]).validate()

    def test_unknown_dsp_is_not_declared_safe(self):
        chain = Chain()
        chain.slots[0] = Slot("chorus.zdl", enabled=False)
        report = chain.dsp_report()
        self.assertIsNone(report["within_limit"])
        self.assertEqual(report["unknown_effect_count"], 1)

    def test_bypassed_effect_still_counts(self):
        chain = Chain()
        chain.slots[0] = Slot("chorus.zdl", enabled=False, dsp_cost=35)
        self.assertEqual(chain.dsp_report()["known_cost_percent_sum"], 35)

    def test_roundtrip(self):
        chain = Chain(name="CE2 test")
        chain.slots[0] = Slot("CE2.zdl", enabled=True, parameters={"Rate": 2.0})
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "test.json"
            chain.save(p)
            self.assertEqual(Chain.load(p), chain)

if __name__ == "__main__":
    unittest.main()
