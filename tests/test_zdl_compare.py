import unittest
from multistomp_lab.zdl_compare import compare_zdl, ComparisonError

class ZDLCompareTests(unittest.TestCase):
    def test_identical(self):
        result = compare_zdl(b'ABC', b'ABC')
        self.assertEqual(result['different_bytes_in_common_prefix'], 0)
        self.assertEqual(result['reported_ranges'], [])

    def test_adjacent_and_separate_changes(self):
        result = compare_zdl(b'abcdefg', b'aXYdeZg')
        self.assertEqual(result['different_bytes_in_common_prefix'], 3)
        self.assertEqual([r['offset'] for r in result['reported_ranges']], [1, 5])
        self.assertEqual(result['reported_ranges'][0]['old_hex'], b'bc'.hex())

    def test_tail(self):
        result = compare_zdl(b'abc', b'abcde')
        self.assertEqual(result['unpaired_tail_bytes'], 2)
        self.assertEqual(result['reported_ranges'][0]['offset'], 3)

    def test_truncated_ranges(self):
        result = compare_zdl(b'abcdef', b'XbXdXf', max_changes=1)
        self.assertTrue(result['ranges_truncated'])
        self.assertEqual(len(result['reported_ranges']), 1)

    def test_no_format_claims(self):
        self.assertFalse(compare_zdl(b'', b'')['format_fields_identified'])

    def test_reject_mutable(self):
        with self.assertRaises(ComparisonError):
            compare_zdl(bytearray(b'a'), b'a')

    def test_reject_limit(self):
        with self.assertRaises(ComparisonError):
            compare_zdl(b'a', b'b', max_changes=0)

if __name__ == '__main__':
    unittest.main()
