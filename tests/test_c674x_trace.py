import unittest
from multistomp_lab.c674x_trace import trace_code_region, TraceError
from multistomp_lab.c674x_scan import PacketScanError


def pack(words):
    return b''.join(w.to_bytes(4, 'little') for w in words)


class TraceTests(unittest.TestCase):
    def test_serial_words(self):
        out = trace_code_region(bytes(32), 0x1000)
        self.assertEqual(len(out), 8)
        self.assertEqual([e.address for e in out], [0x1000 + 4 * i for i in range(8)])

    def test_parallel_pair(self):
        out = trace_code_region(pack([1, 0] + [0] * 6))
        self.assertEqual(out[0].words, (1, 0))
        self.assertEqual(len(out), 7)

    def test_cross_fetch_boundary(self):
        out = trace_code_region(pack([0] * 7 + [1] + [0] * 8))
        self.assertEqual(out[7].address, 28)
        self.assertEqual(out[7].words, (1, 0))

    def test_compact_is_opaque(self):
        out = trace_code_region(pack([0] * 7 + [0xE0000000]))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].kind, 'compact-opaque')

    def test_reject_unfinished(self):
        with self.assertRaises(TraceError):
            trace_code_region(pack([0] * 7 + [1]))

    def test_reject_unaligned_region(self):
        with self.assertRaises(PacketScanError):
            trace_code_region(bytes(31))

    def test_empty(self):
        self.assertEqual(trace_code_region(b''), [])


if __name__ == '__main__':
    unittest.main()
