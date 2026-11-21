import struct
import unittest
from multistomp_lab.zdl_container import parse_zdl_container, ZDLFormatError

def sample(extra=b'', elf=None):
    if elf is None:
        elf = b'\x7fELF' + bytes([1, 1, 1]) + bytes(9) + bytes(36)
    info = b'ZOOM EFFECT DLL SYSTEM VER 1.00\x00' + bytes(8) + b'1.01\x00\x00\x00\x00'
    assert len(info) == 48
    return (bytes(4) + b'SIZE' + struct.pack('<III', 8, 56 + len(extra), len(elf))
            + b'INFO' + struct.pack('<I', 48) + info + extra + elf)

class ZDLContainerTests(unittest.TestCase):
    def test_typical(self):
        r = parse_zdl_container(sample())
        self.assertEqual(r.elf_offset, 76)
        self.assertEqual(r.elf_size, 52)
        self.assertEqual(r.effect_version, '1.01')
        self.assertTrue(r.declared_elf_size_matches_file)

    def test_extended_header(self):
        r = parse_zdl_container(sample(b'BCAB' + bytes(28)))
        self.assertEqual(r.elf_offset, 108)
        self.assertEqual(r.extra_header_size, 32)

    def test_wrong_magic(self):
        with self.assertRaises(ZDLFormatError):
            parse_zdl_container(b'ZDLF' + sample()[4:])

    def test_bad_declared_size(self):
        data = bytearray(sample())
        struct.pack_into('<I', data, 16, 9999)
        with self.assertRaises(ZDLFormatError):
            parse_zdl_container(bytes(data))

    def test_bad_elf(self):
        with self.assertRaises(ZDLFormatError):
            parse_zdl_container(sample(elf=b'NOTELF' + bytes(46)))

    def test_bad_header_size(self):
        data = bytearray(sample())
        struct.pack_into('<I', data, 12, 1)
        with self.assertRaises(ZDLFormatError):
            parse_zdl_container(bytes(data))

    def test_trailing_data_reported(self):
        r = parse_zdl_container(sample() + b'EXTRA')
        self.assertFalse(r.declared_elf_size_matches_file)

if __name__ == '__main__':
    unittest.main()
