"""Read-only ZDL binary map for reverse-engineering, without format guesses.

Produces 32-byte window statistics, printable ASCII spans and SHA-256.
No section is asserted to contain code, and nothing is executed.
"""
from dataclasses import dataclass, asdict
import argparse
import hashlib
import json
import math
from pathlib import Path

MAX_BYTES = 64 * 1024 * 1024

class ZDLMapError(ValueError):
    pass

@dataclass(frozen=True)
class Window:
    offset: int
    length: int
    entropy_bits_per_byte: float
    zero_bytes: int
    printable_bytes: int

def _entropy(chunk: bytes) -> float:
    if not chunk:
        return 0.0
    counts = [0] * 256
    for byte in chunk:
        counts[byte] += 1
    n = len(chunk)
    return round(-sum((c/n) * math.log2(c/n) for c in counts if c), 4)

def map_zdl(blob: bytes, window_size: int = 256, min_string: int = 5) -> dict:
    if not isinstance(blob, bytes) or len(blob) > MAX_BYTES:
        raise ZDLMapError('Expected at most 64 MiB of bytes')
    if type(window_size) is not int or not 32 <= window_size <= 65536 or window_size % 32:
        raise ZDLMapError('Window size must be 32-byte aligned, 32..65536')
    if type(min_string) is not int or not 4 <= min_string <= 256:
        raise ZDLMapError('Minimum string length must be 4..256')
    windows = []
    for offset in range(0, len(blob), window_size):
        chunk = blob[offset:offset + window_size]
        windows.append(asdict(Window(offset, len(chunk), _entropy(chunk),
                                     chunk.count(0), sum(32 <= b <= 126 for b in chunk))))
    strings = []
    start = None
    for i, byte in enumerate(blob):
        if 32 <= byte <= 126:
            if start is None:
                start = i
        elif start is not None:
            if i - start >= min_string:
                strings.append({'offset': start, 'text': blob[start:i].decode('ascii')})
            start = None
    if start is not None and len(blob) - start >= min_string:
        strings.append({'offset': start, 'text': blob[start:].decode('ascii')})
    return {
        'sha256': hashlib.sha256(blob).hexdigest(),
        'size': len(blob),
        'windows': windows,
        'ascii_strings': strings,
        'code_regions_verified': False,
        'zdl_format_verified': False,
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only ZDL binary map')
    parser.add_argument('file', type=Path)
    parser.add_argument('--window', type=int, default=256)
    parser.add_argument('--min-string', type=int, default=5)
    args = parser.parse_args(argv)
    if args.file.stat().st_size > MAX_BYTES:
        parser.error('File exceeds 64 MiB')
    print(json.dumps(map_zdl(args.file.read_bytes(), args.window, args.min_string), indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
