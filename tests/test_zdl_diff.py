import unittest
from multistomp_lab.zdl_diff import compare_bytes

class ZDLDiffTests(unittest.TestCase):
    def test_identical(self):
        r = compare_bytes(b"abcd", b"abcd")
        self.assertEqual(r["changed_bytes"], 0)
        self.assertFalse(r["truncated"])

    def test_changed_and_appended(self):
        r = compare_bytes(b"abcd", b"abXd!")
        self.assertEqual(r["changed_bytes"], 2)
        self.assertEqual(r["shown_changes"], [
            {"offset": 2, "before": "63", "after": "58"},
            {"offset": 4, "before": None, "after": "21"}
        ])

    def test_removed_bytes(self):
        r = compare_bytes(b"abc", b"a")
        self.assertEqual(r["changed_bytes"], 2)
        self.assertEqual(r["shown_changes"][0]["after"], None)

    def test_truncation(self):
        r = compare_bytes(b"aaa", b"bbb", limit=1)
        self.assertEqual(r["changed_bytes"], 3)
        self.assertTrue(r["truncated"])
        self.assertEqual(len(r["shown_changes"]), 1)

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            compare_bytes(b"", b"", limit=-1)

if __name__ == "__main__":
    unittest.main()
