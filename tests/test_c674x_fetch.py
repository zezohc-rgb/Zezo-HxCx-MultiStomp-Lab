import unittest
from multistomp_lab.c674x_fetch import read_standard_packet, read_packets, FetchPacketError

class FetchTests(unittest.TestCase):
    def test_words_little_endian(self):
        data = bytes.fromhex("78563412") + bytes(28)
        p = read_standard_packet(data, 0x1000)
        self.assertEqual(p.words[0], 0x12345678)
        self.assertEqual(len(p.words), 8)
        self.assertEqual(p.address, 0x1000)

    def test_p_bits(self):
        data = (1).to_bytes(4, "little") + (2).to_bytes(4, "little") + bytes(24)
        self.assertEqual(read_standard_packet(data).p_bits[:2], (1, 0))

    def test_alignment(self):
        with self.assertRaises(FetchPacketError):
            read_standard_packet(bytes(32), 4)

    def test_exact_length(self):
        with self.assertRaises(FetchPacketError):
            read_standard_packet(bytes(31))

    def test_multiple_packets(self):
        packets = read_packets(bytes(64), 0x2000)
        self.assertEqual([p.address for p in packets], [0x2000, 0x2020])

    def test_partial_packet_rejected(self):
        with self.assertRaises(FetchPacketError):
            read_packets(bytes(33))

if __name__ == "__main__":
    unittest.main()
