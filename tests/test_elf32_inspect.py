import struct
import unittest
from multistomp_lab.elf32_inspect import inspect_elf32, inspect_zdl_elf, ELFInspectionError

def elf32():
    b = bytearray(92)
    b[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH', b, 16, 3, 140, 1, 0, 0, 52, 0, 52, 0, 0, 40, 1, 0)
    struct.pack_into('<IIIIIIIIII', b, 52, 0, 1, 0, 0, 0, 16, 0, 0, 1, 0)
    return bytes(b)

def zdl(elf):
    info = b'ZOOM EFFECT DLL SYSTEM VER 1.00\x00' + bytes(8) + b'1.01\x00\x00\x00\x00'
    return bytes(4) + b'SIZE' + struct.pack('<III', 8, 56, len(elf)) + b'INFO' + struct.pack('<I', 48) + info + elf

class ELFTests(unittest.TestCase):
    def test_section_inventory(self):
        result = inspect_elf32(elf32())
        self.assertEqual(result['machine'], 140)
        self.assertEqual(result['section_header_count'], 1)
        self.assertEqual(result['sections'][0]['size'], 16)
        self.assertFalse(result['instructions_executed'])

    def test_zdl_integration(self):
        result = inspect_zdl_elf(zdl(elf32()))
        self.assertEqual(result['container']['elf_offset'], 76)
        self.assertEqual(result['elf']['machine'], 140)

    def test_reject_truncated(self):
        with self.assertRaises(ELFInspectionError):
            inspect_elf32(elf32()[:51])

    def test_reject_table_overflow(self):
        b = bytearray(elf32())
        struct.pack_into('<I', b, 32, 900)
        with self.assertRaises(ELFInspectionError):
            inspect_elf32(bytes(b))

    def test_reject_section_outside(self):
        b = bytearray(elf32())
        struct.pack_into('<I', b, 52+16, 900)
        with self.assertRaises(ELFInspectionError):
            inspect_elf32(bytes(b))

    def test_reject_wrong_magic(self):
        with self.assertRaises(ELFInspectionError):
            inspect_elf32(b'NOPE' + elf32()[4:])

if __name__ == '__main__':
    unittest.main()
