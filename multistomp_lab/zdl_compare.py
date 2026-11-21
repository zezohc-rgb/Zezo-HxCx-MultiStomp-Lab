"""Compare two ZDL binaries by byte offset, without guessing format fields."""
from dataclasses import dataclass, asdict
import argparse
import hashlib
import json
from pathlib import Path

MAX_BYTES = 64 * 1024 * 1024

class ComparisonError(ValueError):
    pass

@dataclass(frozen=True)
class Change:
    offset: int
    old_hex: str
    new_hex: str

def compare_zdl(a: bytes, b: bytes, max_changes: int = 128) -> dict:
    if type(a) is not bytes or type(b) is not bytes:
        raise ComparisonError('Both inputs must be immutable bytes')
    if len(a) > MAX_BYTES or len(b) > MAX_BYTES:
        raise ComparisonError('Maximum file size is 64 MiB')
    if type(max_changes) is not int or not 1 <= max_changes <= 4096:
        raise ComparisonError('max_changes must be between 1 and 4096')
    common = min(len(a), len(b))
    changed = sum(a[i] != b[i] for i in range(common))
    ranges = []
    i = 0
    while i < common:
        if a[i] == b[i]:
            i += 1
            continue
        start = i
        while i < common and a[i] != b[i]:
            i += 1
        if len(ranges) < max_changes:
            ranges.append(asdict(Change(start, a[start:i].hex(), b[start:i].hex())))
    # If lengths differ, the tail has no corresponding bytes in the shorter file.
    if len(a) != len(b) and len(ranges) < max_changes:
        ranges.append(asdict(Change(common, a[common:].hex(), b[common:].hex())))
    return {
        'sha256_a': hashlib.sha256(a).hexdigest(),
        'sha256_b': hashlib.sha256(b).hexdigest(),
        'size_a': len(a), 'size_b': len(b),
        'different_bytes_in_common_prefix': changed,
        'unpaired_tail_bytes': abs(len(a) - len(b)),
        'reported_ranges': ranges,
        'ranges_truncated': changed > sum(len(bytes.fromhex(r['old_hex'])) for r in ranges if r['offset'] < common),
        'format_fields_identified': False,
    }

def main(argv=None):
    p = argparse.ArgumentParser(description='Read-only offset comparison of two ZDL files')
    p.add_argument('first', type=Path)
    p.add_argument('second', type=Path)
    p.add_argument('--max-changes', type=int, default=128)
    args = p.parse_args(argv)
    if args.first.stat().st_size > MAX_BYTES or args.second.stat().st_size > MAX_BYTES:
        p.error('Input exceeds 64 MiB')
    print(json.dumps(compare_zdl(args.first.read_bytes(), args.second.read_bytes(),
                                 args.max_changes), indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
