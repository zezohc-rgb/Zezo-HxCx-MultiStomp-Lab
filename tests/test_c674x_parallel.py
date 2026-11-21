import unittest
from multistomp_lab.c674x_parallel import execute_packet, PacketConflict
from multistomp_lab.c674x_state import RegisterFile, TestOperation, UnsupportedOperation

class ParallelTests(unittest.TestCase):
    def test_parallel_reads_snapshot(self):
        r = RegisterFile()
        r.write('A', 0, 5)
        r.write('A', 1, 9)
        execute_packet(r, (
            TestOperation('MVK', ('A', 0), immediate=100),
            TestOperation('ADD', ('A', 2), ('A', 0), ('A', 1)),
        ))
        self.assertEqual(r.read('A', 2), 14)
        self.assertEqual(r.read('A', 0), 100)

    def test_conflict_does_not_commit(self):
        r = RegisterFile()
        with self.assertRaises(PacketConflict):
            execute_packet(r, (
                TestOperation('MVK', ('A', 0), immediate=1),
                TestOperation('MVK', ('A', 0), immediate=2),
            ))
        self.assertEqual(r.read('A', 0), 0)

    def test_bad_second_operation_does_not_commit_first(self):
        r = RegisterFile()
        with self.assertRaises(UnsupportedOperation):
            execute_packet(r, (
                TestOperation('MVK', ('A', 0), immediate=7),
                TestOperation('UNKNOWN', ('B', 0)),
            ))
        self.assertEqual(r.read('A', 0), 0)

    def test_cross_bank(self):
        r = RegisterFile()
        r.write('B', 0, 6)
        execute_packet(r, (TestOperation('ADD', ('A', 1), ('B', 0), ('B', 0)),))
        self.assertEqual(r.read('A', 1), 12)

    def test_too_many(self):
        with self.assertRaises(PacketConflict):
            execute_packet(RegisterFile(), tuple(TestOperation('MVK', ('A', i), immediate=i) for i in range(9)))

    def test_empty(self):
        with self.assertRaises(PacketConflict):
            execute_packet(RegisterFile(), ())

if __name__ == '__main__':
    unittest.main()
