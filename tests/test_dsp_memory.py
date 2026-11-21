import unittest
from multistomp_lab.dsp_memory import DSPMemory, MemoryFault, Region

class DSPMemoryTests(unittest.TestCase):
    def test_little_endian(self):
        m = DSPMemory()
        m.map_region(Region(0x1000, 16))
        m.write_u32(0x1000, 0x12345678)
        self.assertEqual(m.read(0x1000, 4), b"\x78\x56\x34\x12")
        self.assertEqual(m.read_u32(0x1000), 0x12345678)

    def test_read_only(self):
        m = DSPMemory()
        m.map_region(Region(0x2000, 4, False), b"ABCD")
        self.assertEqual(m.read(0x2000, 4), b"ABCD")
        with self.assertRaises(MemoryFault):
            m.write(0x2000, b"X")

    def test_unmapped(self):
        m = DSPMemory()
        m.map_region(Region(0x1000, 8))
        with self.assertRaises(MemoryFault):
            m.read(0x1006, 4)

    def test_unaligned(self):
        m = DSPMemory()
        m.map_region(Region(0x1000, 8))
        with self.assertRaises(MemoryFault):
            m.read_u32(0x1001)

    def test_overlap(self):
        m = DSPMemory()
        m.map_region(Region(0x1000, 8))
        with self.assertRaises(ValueError):
            m.map_region(Region(0x1004, 8))

    def test_overflow(self):
        with self.assertRaises(ValueError):
            Region(0xFFFFFFFE, 4)

if __name__ == "__main__":
    unittest.main()
