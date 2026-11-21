"""Host-side mathematical checks for Zezo CE-2 (not TI DSP emulation)."""
import math
import struct
import unittest

N = 1024

def delay_index(rate, depth, phase):
    if not (0.0 <= phase < 1.0):
        phase = 0.0
    tri = -1.0 + 4.0 * phase if phase < 0.5 else 3.0 - 4.0 * phase
    m = 0.21794872 * depth * tri
    inv = 1.0 + m + m*m + m*m*m + m*m*m*m
    d = 171.99 * inv
    if not (d >= 128.0):
        d = 128.0
    if d > 256.0:
        d = 256.0
    # Round to float32, matching the TI float calculation at the index boundary.
    d = struct.unpack('<f', struct.pack('<f', d))[0]
    bits = struct.unpack('<I', struct.pack('<f', d))[0]
    exponent = (bits >> 23) & 255
    whole = ((bits & 0x7fffff) | 0x800000) >> (150 - exponent)
    frac = d - whole
    return whole, frac

class ChorusMathTests(unittest.TestCase):
    def test_delay_indices_and_fraction(self):
        for rate in (0, .1, .5, 1):
            for depth in (0, .01, .5, 1):
                for i in range(1001):
                    whole, frac = delay_index(rate, depth, i / 1001)
                    self.assertTrue(128 <= whole <= 256)
                    self.assertTrue(0 <= frac < 1)
                    for write in (0, 1, 127, 512, 1023):
                        a = (write + N - whole) & (N-1)
                        b = (a + N - 1) & (N-1)
                        self.assertTrue(0 <= a < N and 0 <= b < N)
    def test_invalid_phase_recovery(self):
        for phase in (float('nan'), float('inf'), -1, 1, 1e30):
            self.assertEqual(delay_index(.5, .5, phase), delay_index(.5, .5, 0))
    def test_depth_zero_constant_delay(self):
        self.assertEqual(len({delay_index(.5, 0, i / 100) for i in range(100)}), 1)
    def test_rate_range(self):
        for rate in (0, .5, 1):
            step = (.30 + 3.20 * rate) * .000022675737
            self.assertTrue(0 < step < 1)

if __name__ == '__main__':
    unittest.main()
