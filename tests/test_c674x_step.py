import unittest
from multistomp_lab.c674x_step import CLRStepper
from multistomp_lab.c674x_clr import DecodeError

def clr(dst, src, lo, hi, side=0):
    return (dst << 23) | (src << 18) | (lo << 13) | (hi << 8) | (0b110010 << 2) | (side << 1)

class StepperTests(unittest.TestCase):
    def test_real_encoded_word(self):
        m = CLRStepper()
        m.registers.write('A', 1, 0xffffffff)
        self.assertEqual(m.step_word(clr(2, 1, 4, 7)), 0xffffff0f)
        self.assertEqual(m.registers.read('A', 2), 0xffffff0f)
        self.assertEqual(m.instructions_retired, 1)

    def test_stream(self):
        m = CLRStepper()
        m.registers.write('B', 1, 0xffffffff)
        code = b''.join(w.to_bytes(4, 'little') for w in (clr(2, 1, 0, 7, 1), clr(3, 2, 8, 15, 1)))
        self.assertEqual(m.step_bytes(code), [0xffffff00, 0xffff0000])
        self.assertEqual(m.instructions_retired, 2)

    def test_rejects_unknown_without_mutation(self):
        m = CLRStepper()
        m.registers.write('A', 1, 0xffffffff)
        code = clr(2, 1, 0, 7).to_bytes(4, 'little') + bytes(4)
        with self.assertRaises(DecodeError):
            m.step_bytes(code)
        self.assertEqual(m.registers.read('A', 2), 0)
        self.assertEqual(m.instructions_retired, 0)

    def test_rejects_parallel(self):
        with self.assertRaises(DecodeError):
            CLRStepper().step_word(clr(2, 1, 0, 7) | 1)

    def test_rejects_partial_word(self):
        with self.assertRaises(DecodeError):
            CLRStepper().step_bytes(b'abc')

if __name__ == '__main__':
    unittest.main()
