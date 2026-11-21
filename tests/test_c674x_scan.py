import unittest
from multistomp_lab.c674x_scan import scan_code_region, PacketScanError

def pack(words):
    return b''.join(x.to_bytes(4, 'little') for x in words)

class ScanTests(unittest.TestCase):
    def test_standard(self):
        p = scan_code_region(bytes(32), 0x1000)[0]
        self.assertEqual((p.kind, p.address, p.instruction_widths), ('standard', 0x1000, (32,) * 8))

    def test_compact(self):
        p = scan_code_region(pack([0] * 7 + [0xE0000000 | (0b101 << 21)]))[0]
        self.assertEqual(p.kind, 'compact-header')
        self.assertEqual(p.instruction_widths, (16, 16, 32, 16, 16, 32, 32, 32, 32))

    def test_two_packets(self):
        self.assertEqual([p.address for p in scan_code_region(bytes(64), 0x2000)], [0x2000, 0x2020])

    def test_alignment(self):
        with self.assertRaises(PacketScanError):
            scan_code_region(bytes(32), 4)

    def test_truncated(self):
        with self.assertRaises(PacketScanError):
            scan_code_region(bytes(31))

    def test_empty(self):
        self.assertEqual(scan_code_region(b''), [])

if __name__ == '__main__':
    unittest.main()
