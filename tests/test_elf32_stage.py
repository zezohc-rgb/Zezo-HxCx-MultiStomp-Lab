import struct
import unittest
from multistomp_lab.elf32_stage import stage_elf32, read_staged
from multistomp_lab.elf32_inspect import ELFInspectionError

def elf_fixture():
    b = bytearray(256)
    b[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH', b, 16, 3, 140, 1, 0, 0, 52, 0, 52, 0, 0, 40, 3, 0)
    struct.pack_into('<IIIIIIIIII', b, 92, 0, 1, 6, 0x1000, 192, 32, 0, 0, 32, 0)
    struct.pack_into('<IIIIIIIIII', b, 132, 0, 8, 3, 0x2000, 0, 64, 0, 0, 32, 0)
    b[192:224] = bytes(range(32))
    return bytes(b)

class StageTests(unittest.TestCase):
    def test_copy_code(self):
        images = stage_elf32(elf_fixture())
        self.assertEqual(read_staged(images, 0x1000, 4), bytes(range(4)))
        self.assertTrue(images[0].executable)

    def test_zero_fill(self):
        images = stage_elf32(elf_fixture())
        self.assertEqual(read_staged(images, 0x2000, 64), bytes(64))
        self.assertTrue(images[1].writable)

    def test_unmapped_rejected(self):
        with self.assertRaises(ELFInspectionError):
            read_staged(stage_elf32(elf_fixture()), 0x3000, 4)

    def test_cross_section_rejected(self):
        with self.assertRaises(ELFInspectionError):
            read_staged(stage_elf32(elf_fixture()), 0x101f, 2)

    def test_overflow_rejected(self):
        with self.assertRaises(ELFInspectionError):
            read_staged(stage_elf32(elf_fixture()), 0xffffffff, 2)

if __name__ == '__main__':
    unittest.main()
