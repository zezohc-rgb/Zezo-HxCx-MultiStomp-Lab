import unittest
from multistomp_lab.c674x_packets import group_execute_packets, UnsupportedPacket

def binary(*words):
    return b"".join(w.to_bytes(4, "little") for w in words)

class PacketGroupingTests(unittest.TestCase):
    def test_serial(self):
        groups = group_execute_packets(binary(*([0] * 8)))
        self.assertEqual([len(x) for x in groups], [1] * 8)

    def test_parallel_pairs(self):
        groups = group_execute_packets(binary(1, 0, 1, 0, 1, 0, 1, 0))
        self.assertEqual([len(x) for x in groups], [2, 2, 2, 2])
        self.assertEqual(groups[0][1].address, 4)

    def test_cross_fetch_boundary(self):
        data = binary(*([0] * 7), 1) + binary(*([0] * 8))
        groups = group_execute_packets(data)
        self.assertEqual([len(x) for x in groups][-9:], [2] + [1] * 7)

    def test_compact_header_rejected(self):
        with self.assertRaises(UnsupportedPacket):
            group_execute_packets(binary(*([0] * 7), 0xE0000000))

    def test_unterminated(self):
        with self.assertRaises(UnsupportedPacket):
            group_execute_packets(binary(*([0] * 7), 1))

    def test_more_than_eight(self):
        data = binary(*([1] * 8)) + binary(*([0] * 8))
        with self.assertRaises(UnsupportedPacket):
            group_execute_packets(data)

if __name__ == "__main__":
    unittest.main()
