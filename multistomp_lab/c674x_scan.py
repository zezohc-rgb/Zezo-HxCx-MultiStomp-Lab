"""Conservative C674x fetch-packet inventory for an already identified code region.

This is not a ZDL parser or an opcode decoder. Binary regions must be supplied
by the caller; arbitrary ZDL bytes must not be treated as executable code.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import json

class PacketScanError(ValueError):
    pass

@dataclass(frozen=True)
class PacketSummary:
    address: int
    kind: str
    instruction_widths: tuple[int, ...]
    raw_words: tuple[int, ...]

def scan_code_region(data: bytes, base_address: int = 0) -> list[PacketSummary]:
    if not isinstance(base_address, int) or base_address < 0 or base_address % 32:
        raise PacketScanError('base address must be nonnegative and 32-byte aligned')
    if len(data) % 32:
        raise PacketScanError('code region length must be a multiple of 32 bytes')
    if len(data) > 64 * 1024 * 1024:
        raise PacketScanError('code region exceeds 64 MiB')
    packets = []
    for offset in range(0, len(data), 32):
        words = tuple(int.from_bytes(data[offset + i:offset + i + 4], 'little') for i in range(0, 32, 4))
        if words[7] >> 28 == 0xE:
            layout = (words[7] >> 21) & 0x7f
            widths = tuple(width for i in range(7) for width in ((16, 16) if layout & (1 << i) else (32,)))
            kind = 'compact-header'
        else:
            widths = (32,) * 8
            kind = 'standard'
        packets.append(PacketSummary(base_address + offset, kind, widths, words))
    return packets

def main():
    p = argparse.ArgumentParser(description='Inspect aligned C674x code-region packet layout')
    p.add_argument('file', type=Path, help='pre-extracted, independently identified code region')
    p.add_argument('--base', type=lambda x: int(x, 0), default=0)
    args = p.parse_args()
    try:
        if args.file.stat().st_size > 64 * 1024 * 1024:
            raise PacketScanError('file exceeds 64 MiB')
        result = scan_code_region(args.file.read_bytes(), args.base)
        print(json.dumps([asdict(x) for x in result], indent=2))
    except (OSError, ValueError) as exc:
        p.exit(1, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
