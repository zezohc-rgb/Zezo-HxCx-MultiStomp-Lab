import unittest
from multistomp_lab.c674x_region_step import RegionStepper, UnsupportedCodeRegion
from multistomp_lab.c674x_clr import DecodeError

def clr(dst, src, lo, hi):
    return (dst << 23) | (src << 18) | (lo << 13) | (hi << 8) | (0b110010 << 2)

def pack(words):
    return b''.join(w.to_bytes(4, 'little') for w in words)

class RegionStepperTests(unittest.TestCase):
    def test_serial_clr_fetch_packet(self):
        m = RegionStepper()
        m.registers.write('A', 1, 0xffffffff)
        code = pack([clr(2, 1, 0, 7), clr(3, 2, 8, 15)] + [clr(4, 4, 0, 0)] * 6)
        values = m.execute(code, 0x1000)
        self.assertEqual(values[:2], (0xffffff00, 0xffff0000))
        self.assertEqual(m.retired, 8)

    def test_reject_unknown_before_mutation(self):
        m = RegionStepper()
        m.registers.write('A', 1, 0xffffffff)
        code = pack([clr(2, 1, 0, 7), 0] + [clr(4, 4, 0, 0)] * 6)
        with self.assertRaises(DecodeError):
            m.execute(code)
        self.assertEqual(m.registers.read('A', 2), 0)
        self.assertEqual(m.retired, 0)

    def test_reject_parallel_packet(self):
        m = RegionStepper()
        code = pack([clr(2, 1, 0, 7) | 1, clr(3, 2, 8, 15)] + [clr(4, 4, 0, 0)] * 6)
        with self.assertRaises(UnsupportedCodeRegion):
            m.execute(code)
        self.assertEqual(m.retired, 0)

    def test_reject_compact_packet(self):
        with self.assertRaises(UnsupportedCodeRegion):
            RegionStepper().execute(pack([0] * 7 + [0xE0000000]))

    def test_empty(self):
        m = RegionStepper()
        self.assertEqual(m.execute(b''), ())
        self.assertEqual(m.retired, 0)

if __name__ == '__main__':
    unittest.main()
