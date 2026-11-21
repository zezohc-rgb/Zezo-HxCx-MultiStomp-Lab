"""Read-only ZDL binary reconnaissance.

This module does not assert a ZDL layout or execute DSP code. It extracts
candidate signatures and ASCII spans for subsequent format research.
"""
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import json
import re

MAX_FILE_SIZE = 64 * 1024 * 1024
ASCII_PATTERN = re.compile(rb"[\x20-\x7e]{5,}")

@dataclass(frozen=True)
class ProbeResult:
    filename: str
    size: int
    sha256: str
    prefix_hex: str
    printable_strings: list[dict]
    format_verified: bool = False
    executable: bool = False

def probe_bytes(data: bytes, filename: str = "<memory>", max_strings: int = 100) -> ProbeResult:
    if not 4 <= len(data) <= MAX_FILE_SIZE:
        raise ValueError("ZDL candidate must be between 4 bytes and 64 MiB")
    if not 0 <= max_strings <= 1000:
        raise ValueError("max_strings out of range")
    strings = [
        {"offset": match.start(), "text": match.group().decode("ascii")}
        for match in ASCII_PATTERN.finditer(data)
    ][:max_strings]
    return ProbeResult(filename, len(data), sha256(data).hexdigest(),
                       data[:64].hex(" "), strings)

def probe_file(path: str | Path, max_strings: int = 100) -> ProbeResult:
    path = Path(path)
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    return probe_bytes(path.read_bytes(), path.name, max_strings)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Read-only reconnaissance of a ZDL binary")
    parser.add_argument("file", type=Path)
    parser.add_argument("--max-strings", type=int, default=100)
    args = parser.parse_args()
    try:
        print(json.dumps(asdict(probe_file(args.file, args.max_strings)), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")

if __name__ == "__main__":
    main()
