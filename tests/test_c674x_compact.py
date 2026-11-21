import unittest
from multistomp_lab.c674x_compact import (
    CompactHeaderError, parse_compact_header, inspect_compact_fetch_packet,
)

class CompactTests(unittest.TestCase):
    def test_header_fields(self):
        h = parse_compact_header(0xE0000000 | (0x55 << 21) | (0x23 << 14) | 0x1234)
        self.assertEqual((h.layout, h.expansion, h.parallel_bits), (0x55, 0x23, 0x1234))

    def test_reject_nonheader(self):
        with self.assertRaises(CompactHeaderError):
            parse_compact_header(0)

    def test_reject_out_of_range(self):
        with self.assertRaises(CompactHeaderError):
            parse_compact_header(1 << 32)

    def test_split_compact_words(self):
        words = [0x12345678] + [0] * 6 + [0xE0000000 | (1 << 21)]
        data = b"".join(x.to_bytes(4, "little") for x in words)
        result = inspect_compact_fetch_packet(data)
        self.assertEqual(result["instructions"][0], {"word": 0, "width": 16, "raw": [0x5678, 0x1234]})
        self.assertEqual(result["instructions"][1]["width"], 32)
        self.assertFalse(result["decoded"])

    def test_reject_wrong_length(self):
        with self.assertRaises(CompactHeaderError):
            inspect_compact_fetch_packet(bytes(31))

if __name__ == "__main__":
    unittest.main()
