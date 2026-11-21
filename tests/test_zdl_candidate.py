import hashlib
import unittest
from multistomp_lab.zdl_candidate import extract_candidate_region, ExtractionError

class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.blob = bytes(range(128))

    def test_extract_and_hash(self):
        region = extract_candidate_region(self.blob, 32, 64)
        self.assertEqual(region.data, self.blob[32:96])
        self.assertEqual(region.source_sha256, hashlib.sha256(self.blob).hexdigest())
        self.assertEqual(region.region_sha256, hashlib.sha256(self.blob[32:96]).hexdigest())

    def test_source_digest_guard(self):
        with self.assertRaises(ExtractionError):
            extract_candidate_region(self.blob, 0, 32, '0' * 64)

    def test_out_of_bounds(self):
        with self.assertRaises(ExtractionError):
            extract_candidate_region(self.blob, 96, 64)

    def test_reject_unaligned(self):
        with self.assertRaises(ExtractionError):
            extract_candidate_region(self.blob, 1, 32)

    def test_reject_zero_length(self):
        with self.assertRaises(ExtractionError):
            extract_candidate_region(self.blob, 0, 0)

    def test_reject_boolean_offset(self):
        with self.assertRaises(ExtractionError):
            extract_candidate_region(self.blob, True, 32)

    def test_reject_nonbytes(self):
        with self.assertRaises(ExtractionError):
            extract_candidate_region(bytearray(self.blob), 0, 32)

if __name__ == '__main__':
    unittest.main()
