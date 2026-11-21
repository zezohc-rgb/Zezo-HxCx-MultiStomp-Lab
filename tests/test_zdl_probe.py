import hashlib
import unittest
from multistomp_lab.zdl_probe import probe_bytes

class ProbeTests(unittest.TestCase):
    def test_ascii_offsets_and_hash(self):
        data = b"\x00\x01ZDL_TEST\x00\xff"
        result = probe_bytes(data, "fixture.zdl")
        self.assertEqual(result.size, len(data))
        self.assertEqual(result.sha256, hashlib.sha256(data).hexdigest())
        self.assertEqual(result.printable_strings, [{"offset": 2, "text": "ZDL_TEST"}])
        self.assertFalse(result.format_verified)
        self.assertFalse(result.executable)

    def test_reject_oversized_input(self):
        with self.assertRaises(ValueError):
            probe_bytes(b"x" * (64 * 1024 * 1024 + 1))

    def test_limit_strings(self):
        result = probe_bytes(b"abcde\x00fghij", max_strings=1)
        self.assertEqual(len(result.printable_strings), 1)

if __name__ == "__main__":
    unittest.main()
