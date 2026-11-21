import unittest
from multistomp_lab.c674x_clr import DecodeError, decode_clr_constant, execute_clr_constant
from multistomp_lab.c674x_state import RegisterFile


def encode(dst, src, lo, hi, side=0, parallel=0, condition=0):
    return ((condition << 28) | (dst << 23) | (src << 18) |
            (lo << 13) | (hi << 8) | (0b110010 << 2) | (side << 1) | parallel)


class ClrTests(unittest.TestCase):
    def test_decode_fields(self):
        self.assertEqual(decode_clr_constant(encode(3, 4, 5, 9)).destination, 3)
        self.assertEqual(decode_clr_constant(encode(3, 4, 5, 9)).source, 4)

    def test_clear_middle_bits(self):
        r = RegisterFile()
        r.write('A', 4, 0xffffffff)
        self.assertEqual(execute_clr_constant(r, decode_clr_constant(encode(3, 4, 5, 9))),
                         0xfffffc1f)

    def test_side_b(self):
        r = RegisterFile()
        r.write('B', 2, 0xffffffff)
        execute_clr_constant(r, decode_clr_constant(encode(1, 2, 0, 31, side=1)))
        self.assertEqual(r.read('B', 1), 0)
        self.assertEqual(r.read('A', 1), 0)

    def test_inverted_range_unchanged(self):
        r = RegisterFile()
        r.write('A', 2, 0x12345678)
        self.assertEqual(execute_clr_constant(r, decode_clr_constant(encode(1, 2, 9, 5))),
                         0x12345678)

    def test_reject_other_opcode(self):
        with self.assertRaises(DecodeError):
            decode_clr_constant(0)

    def test_reject_parallel(self):
        with self.assertRaises(DecodeError):
            decode_clr_constant(encode(1, 2, 0, 2, parallel=1))

    def test_reject_conditional(self):
        with self.assertRaises(DecodeError):
            decode_clr_constant(encode(1, 2, 0, 2, condition=1))

    def test_reject_out_of_range(self):
        with self.assertRaises(DecodeError):
            decode_clr_constant(-1)


if __name__ == '__main__':
    unittest.main()
