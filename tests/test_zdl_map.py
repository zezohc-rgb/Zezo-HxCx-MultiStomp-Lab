import hashlib
import unittest
from multistomp_lab.zdl_map import map_zdl, ZDLMapError

class ZDLMapTests(unittest.TestCase):
    def test_empty(self):
        result = map_zdl(b'')
        self.assertEqual(result['windows'], [])
        self.assertEqual(result['ascii_strings'], [])
        self.assertEqual(result['sha256'], hashlib.sha256(b'').hexdigest())

    def test_windows_and_tail(self):
        result = map_zdl(bytes(65), window_size=32)
        self.assertEqual([w['length'] for w in result['windows']], [32, 32, 1])
        self.assertEqual(result['windows'][0]['zero_bytes'], 32)
        self.assertEqual(result['windows'][0]['entropy_bits_per_byte'], 0.0)

    def test_strings_and_offsets(self):
        result = map_zdl(b'\x00HELLO\x00WORLD!', min_string=5)
        self.assertEqual(result['ascii_strings'], [
            {'offset': 1, 'text': 'HELLO'}, {'offset': 7, 'text': 'WORLD!'}])

    def test_no_claims_of_verified_format(self):
        result = map_zdl(b'ZDL' + bytes(29))
        self.assertFalse(result['code_regions_verified'])
        self.assertFalse(result['zdl_format_verified'])

    def test_reject_bad_window(self):
        with self.assertRaises(ZDLMapError):
            map_zdl(bytes(32), window_size=31)

    def test_reject_bad_min_string(self):
        with self.assertRaises(ZDLMapError):
            map_zdl(bytes(32), min_string=1)

    def test_reject_mutable_input(self):
        with self.assertRaises(ZDLMapError):
            map_zdl(bytearray(32))

if __name__ == '__main__':
    unittest.main()
