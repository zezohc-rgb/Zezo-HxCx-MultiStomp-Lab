import unittest
from multistomp_lab.c674x_state import RegisterFile, TestOperation, execute_test_operation, UnsupportedOperation

class RegisterTests(unittest.TestCase):
    def test_bank_isolation(self):
        r = RegisterFile()
        r.write('A', 3, 7)
        self.assertEqual(r.read('B', 3), 0)
        self.assertEqual(r.read('A', 3), 7)

    def test_wrap(self):
        r = RegisterFile()
        r.write('A', 0, 0x100000001)
        self.assertEqual(r.read('A', 0), 1)

    def test_invalid_index(self):
        with self.assertRaises(ValueError):
            RegisterFile().read('A', 32)

    def test_mvk(self):
        r = RegisterFile()
        self.assertEqual(execute_test_operation(r, TestOperation('MVK', ('B', 2), immediate=-1)), 0xffffffff)

    def test_add_wrap(self):
        r = RegisterFile()
        r.write('A', 0, 0xffffffff)
        r.write('A', 1, 2)
        self.assertEqual(execute_test_operation(r, TestOperation('ADD', ('A', 2), ('A', 0), ('A', 1))), 1)

    def test_sub_wrap(self):
        r = RegisterFile()
        r.write('A', 0, 0)
        r.write('A', 1, 1)
        self.assertEqual(execute_test_operation(r, TestOperation('SUB', ('A', 2), ('A', 0), ('A', 1))), 0xffffffff)

    def test_boolean_ops(self):
        r = RegisterFile()
        r.write('A', 0, 0b1010)
        r.write('A', 1, 0b1100)
        for name, expected in [('AND', 0b1000), ('OR', 0b1110), ('XOR', 0b0110)]:
            self.assertEqual(execute_test_operation(r, TestOperation(name, ('A', 2), ('A', 0), ('A', 1))), expected)

    def test_unknown_rejected(self):
        with self.assertRaises(UnsupportedOperation):
            execute_test_operation(RegisterFile(), TestOperation('MAGIC', ('A', 0)))

    def test_no_partial_write_on_bad_source(self):
        r = RegisterFile()
        r.write('A', 2, 55)
        with self.assertRaises(ValueError):
            execute_test_operation(r, TestOperation('ADD', ('A', 2), ('A', 0), ('B', 32)))
        self.assertEqual(r.read('A', 2), 55)

if __name__ == '__main__':
    unittest.main()
