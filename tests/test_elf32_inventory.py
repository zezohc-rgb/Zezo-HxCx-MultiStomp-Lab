import struct
import unittest
from multistomp_lab.elf32_inventory import inventory_elf32
from multistomp_lab.elf32_inspect import ELFInspectionError

def make_elf(relocation_entry_size=8, relocation_target=1):
    b = bytearray(256)
    b[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH', b, 16, 3, 140, 1, 0, 0, 52, 0, 52, 0, 0, 40, 3, 0)
    # section 1: executable code, offset 192, 32 bytes
    struct.pack_into('<IIIIIIIIII', b, 92, 0, 1, 6, 0x1000, 192, 32, 0, 0, 32, 0)
    # section 2: relocation table, offset 224, 8 bytes
    struct.pack_into('<IIIIIIIIII', b, 132, 0, 9, 0, 0, 224, 8, 0, relocation_target, 4, relocation_entry_size)
    return bytes(b)

class InventoryTests(unittest.TestCase):
    def test_executable_and_relocation(self):
        result = inventory_elf32(make_elf())
        self.assertEqual(result['executable_sections'][0]['file_offset'], 192)
        self.assertTrue(result['executable_sections'][0]['aligned_to_32_bytes'])
        self.assertEqual(result['relocation_tables'][0]['entries'], 1)
        self.assertFalse(result['relocations_applied'])

    def test_reject_bad_relocation_size(self):
        with self.assertRaises(ELFInspectionError):
            inventory_elf32(make_elf(relocation_entry_size=4))

    def test_reject_bad_relocation_target(self):
        with self.assertRaises(ELFInspectionError):
            inventory_elf32(make_elf(relocation_target=10))

    def test_reject_truncated_elf(self):
        with self.assertRaises(ELFInspectionError):
            inventory_elf32(b'bad')

if __name__ == '__main__':
    unittest.main()
