import io
import struct
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from multistomp_lab.zdl_cli import inspect_file, main

def sample():
    elf = bytearray(92)
    elf[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH', elf, 16, 3, 140, 1, 0, 0, 52, 0, 52, 0, 0, 40, 1, 0)
    info = b'ZOOM EFFECT DLL SYSTEM VER 1.00\x00' + bytes(8) + b'1.01\x00\x00\x00\x00'
    return bytes(4) + b'SIZE' + struct.pack('<III', 8, 56, len(elf)) + b'INFO' + struct.pack('<I', 48) + info + elf

class CLITests(unittest.TestCase):
    def test_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.zdl'
            path.write_bytes(sample())
            result = inspect_file(str(path))
            self.assertEqual(result['container']['elf_offset'], 76)
            self.assertEqual(result['runtime_status'], 'inspection_only_not_executable')

    def test_json_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.zdl'
            out = Path(directory) / 'report.json'
            path.write_bytes(sample())
            self.assertEqual(main([str(path), '--output', str(out)]), 0)
            self.assertIn('inspection_only_not_executable', out.read_text())

    def test_invalid_file_returns_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.zdl'
            path.write_bytes(b'bad')
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(path)]), 2)

    def test_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.zdl'
            path.write_bytes(sample())
            stream = io.StringIO()
            with redirect_stdout(stream):
                self.assertEqual(main([str(path)]), 0)
            self.assertIn('elf_header', stream.getvalue())

if __name__ == '__main__':
    unittest.main()
