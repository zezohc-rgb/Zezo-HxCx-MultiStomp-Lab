import unittest
from multistomp_lab.c674x_harness import MemoryOperation, TestMachine
from multistomp_lab.c674x_state import TestOperation
from multistomp_lab.dsp_memory import MemoryFault, Region

class HarnessTests(unittest.TestCase):
    def test_store_load_and_arithmetic(self):
        m = TestMachine()
        m.memory.map_region(Region(0x1000, 16))
        m.step(TestOperation('MVK', ('A', 0), immediate=123))
        m.step(MemoryOperation('STW', ('A', 0), 0x1000))
        m.step(MemoryOperation('LDW', ('B', 1), 0x1000))
        m.step(TestOperation('ADD', ('A', 2), ('A', 0), ('B', 1)))
        self.assertEqual(m.registers.read('A', 2), 246)
        self.assertEqual(m.memory.read_u32(0x1000), 123)
        self.assertEqual(m.steps, 4)

    def test_unmapped_store_fails_without_step(self):
        m = TestMachine()
        m.registers.write('A', 0, 9)
        with self.assertRaises(MemoryFault):
            m.step(MemoryOperation('STW', ('A', 0), 0x1000))
        self.assertEqual(m.steps, 0)

    def test_readonly_store_fails(self):
        m = TestMachine()
        m.memory.map_region(Region(0x1000, 4, False))
        with self.assertRaises(MemoryFault):
            m.step(MemoryOperation('STW', ('A', 0), 0x1000))

    def test_unknown_operation_rejected(self):
        m = TestMachine()
        with self.assertRaises(ValueError):
            m.step(MemoryOperation('NOP?', ('A', 0), 0))
        self.assertEqual(m.steps, 0)

    def test_bad_operation_type(self):
        with self.assertRaises(TypeError):
            TestMachine().step('ADD')

if __name__ == '__main__':
    unittest.main()
