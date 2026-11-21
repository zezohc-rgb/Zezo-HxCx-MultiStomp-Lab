import struct
import unittest
from multistomp_lab.elf32_load_plan import plan_elf32_sections
from multistomp_lab.elf32_inspect import ELFInspectionError

def fixture(overlap=False, huge=False, bad_alignment=False):
    b = bytearray(256)
    b[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH', b, 16,
                     3, 140, 1, 0, 0, 52, 0, 52, 0, 0, 40, 3, 0)
    struct.pack_into('<IIIIIIIIII', b, 92, 0, 1, 6, 0x1000,
                     192, 32, 0, 0, 8192 if bad_alignment else 32, 0)
    struct.pack_into('<IIIIIIIIII', b, 132, 0, 8, 3,
                     0x1010 if overlap else 0x2000,
                     0, 0xffffffff if huge else 64, 0, 0, 32, 0)
    return bytes(b)

class ELFLoadPlanTests(unittest.TestCase):
    def test_allocated_code_and_zero_fill(self):
        plan = plan_elf32_sections(fixture())
        self.assertEqual(plan['total_allocated_bytes'], 96)
        self.assertEqual(len(plan['sections']), 2)
        self.assertTrue(plan['sections'][0]['executable'])
        self.assertFalse(plan['sections'][0]['writable'])
        self.assertTrue(plan['sections'][1]['zero_fill'])
        self.assertIsNone(plan['sections'][1]['source_offset'])
        self.assertFalse(plan['memory_mutated'])

    def test_overlap_rejected(self):
        with self.assertRaises(ELFInspectionError):
            plan_elf32_sections(fixture(overlap=True))

    def test_oversize_rejected(self):
        with self.assertRaises(ELFInspectionError):
            plan_elf32_sections(fixture(huge=True))

    def test_bad_alignment_rejected(self):
        with self.assertRaises(ELFInspectionError):
            plan_elf32_sections(fixture(bad_alignment=True))

    def test_non_c6000_elf_rejected(self):
        data = bytearray(fixture())
        struct.pack_into('<H', data, 18, 3)
        with self.assertRaises(ELFInspectionError):
            plan_elf32_sections(bytes(data))

    def test_truncated_rejected(self):
        with self.assertRaises(ELFInspectionError):
            plan_elf32_sections(b'bad')

if __name__ == '__main__':
    unittest.main()
