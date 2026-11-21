import hashlib
import unittest
from multistomp_lab.zdl_inspect import inspect_candidate
from multistomp_lab.zdl_candidate import ExtractionError

def clr():
    return (2 << 23) | (1 << 18) | (0b110010 << 2)

class ZDLInspectTests(unittest.TestCase):
    def setUp(self):
        self.blob = b'ZDL?' + bytes(28) + b''.join(clr().to_bytes(4, 'little') for _ in range(8))

    def test_candidate_pipeline(self):
        result = inspect_candidate(self.blob, 32, 32)
        self.assertEqual(result['source_offset'], 32)
        self.assertEqual(result['analysis']['supported_packets'], 8)
        self.assertFalse(result['region_is_verified_code'])
        self.assertFalse(result['decoder_is_independently_validated'])

    def test_sha_guard(self):
        with self.assertRaises(ExtractionError):
            inspect_candidate(self.blob, 32, 32, '0' * 64)

    def test_correct_sha(self):
        result = inspect_candidate(self.blob, 32, 32, hashlib.sha256(self.blob).hexdigest())
        self.assertEqual(result['region_length'], 32)

    def test_invalid_alignment(self):
        with self.assertRaises(ExtractionError):
            inspect_candidate(self.blob, 4, 32)

    def test_invalid_range(self):
        with self.assertRaises(ExtractionError):
            inspect_candidate(self.blob, 32, 64)

if __name__ == '__main__':
    unittest.main()
