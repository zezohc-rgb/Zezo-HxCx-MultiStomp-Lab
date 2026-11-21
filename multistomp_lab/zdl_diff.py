"""Byte-level ZDL comparison for reverse-engineering experiments.

No undocumented header fields are assumed. Differences are raw byte offsets,
not inferred DSP instructions or parameter locations.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import json

MAX_BYTES = 64 * 1024 * 1024

@dataclass(frozen=True)
class Difference:
    offset: int
    before: str | None
    after: str | None

def compare_bytes(before: bytes, after: bytes, limit: int = 256) -> dict:
    if not 0 <= limit <= 10000:
        raise ValueError("limit must be between 0 and 10000")
    if len(before) > MAX_BYTES or len(after) > MAX_BYTES:
        raise ValueError("file exceeds 64 MiB limit")
    shared = min(len(before), len(after))
    changed_shared = sum(a != b for a, b in zip(before[:shared], after[:shared]))
    total_changes = changed_shared + abs(len(before) - len(after))
    changes = []
    for offset in range(max(len(before), len(after))):
        a = before[offset] if offset < len(before) else None
        b = after[offset] if offset < len(after) else None
        if a != b:
            if len(changes) < limit:
                changes.append(asdict(Difference(offset,
                    f"{a:02x}" if a is not None else None,
                    f"{b:02x}" if b is not None else None)))
            elif total_changes == 0:
                break
    return {
        "before_size": len(before), "after_size": len(after),
        "changed_bytes": total_changes,
        "shown_changes": changes,
        "truncated": total_changes > len(changes),
        "interpretation": "Raw byte offsets only; no ZDL field semantics inferred."
    }

def _read(path: Path) -> bytes:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"File too large: {path}")
    return path.read_bytes()

def main():
    parser = argparse.ArgumentParser(description="Compare two ZDL binaries byte by byte")
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--limit", type=int, default=256)
    args = parser.parse_args()
    try:
        print(json.dumps(compare_bytes(_read(args.before), _read(args.after), args.limit), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")

if __name__ == "__main__":
    main()
