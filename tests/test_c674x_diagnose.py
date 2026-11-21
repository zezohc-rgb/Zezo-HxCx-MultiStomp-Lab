import unittest
from multistomp_lab.c674x_diagnose import diagnose

def pack(words):
    return b''.join(w.to_bytes(4, 'little') for w in words)

def clr(dst=2, src=1, lo=0, hi=7):
    return (dst << 23) | (src << 18) | (lo << 13) | (hi << 8) | (0b110010 << 2)

class DiagnoseTests(unittest.TestCase):
    def test_reports_supported_clr_without_execution(self):
        report = diagnose(pack([clr()] * 8), 0x1000)
        self.assertEqual(report["supported_packets"], 8)
        self.assertEqual(report["details"][0]["address"], "0x00001000")
        self.assertFalse(report["independent_opcode_validation"])
        self.assertFalse(report["executable_as_zdl"])

    def test_reports_unknown_opcode(self):
        report = diagnose(bytes(32))
        self.assertEqual(report["supported_packets"], 0)
        self.assertEqual(report["details"][0]["reason"], "unsupported or unknown instruction")

    def test_reports_compact_opaque(self):
        report = diagnose(pack([0] * 7 + [0xe0000000]))
        self.assertEqual(report["details"][0]["reason"], "compact or parallel packet not supported")

    def test_reports_parallel_opaque(self):
        report = diagnose(pack([clr() | 1, clr()] + [clr()] * 6))
        self.assertFalse(report["details"][0]["supported"])

    def test_empty(self):
        self.assertEqual(diagnose(b"")["packets"], 0)

if __name__ == "__main__":
    unittest.main()
