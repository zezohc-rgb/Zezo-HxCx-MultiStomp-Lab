"""Safe initial inspection of ZDL files; does not execute DSP code.

Usage: python tools/inspect_zdl.py path/to/effect.zdl
"""
import argparse
import hashlib
import json
from pathlib import Path


def inspect(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    size = path.stat().st_size
    if size < 4:
        raise ValueError("File too small to inspect")
    if size > 64 * 1024 * 1024:
        raise ValueError("File exceeds 64 MiB safety limit")
    data = path.read_bytes()
    return {
        "filename": path.name,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "first_16_bytes_hex": data[:16].hex(" "),
        "format_verified": False,
        "dsp_executable": False,
        "note": "Metadata only; ZDL format parsing and C674x execution are not implemented yet.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a ZDL file without executing it")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.file), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
