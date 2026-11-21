"""Read-only ZDL candidate-region inspection pipeline.

A user-supplied offset and length are *hypotheses*, not a validated ZDL
format. This tool never runs binary code or alters the source file.
"""
import argparse
import json
from pathlib import Path
from .zdl_candidate import extract_candidate_region
from .c674x_diagnose import diagnose

def inspect_candidate(blob: bytes, offset: int, length: int,
                      expected_sha256: str | None = None,
                      base_address: int = 0) -> dict:
    region = extract_candidate_region(blob, offset, length, expected_sha256)
    result = diagnose(region.data, base_address)
    return {
        "source_sha256": region.source_sha256,
        "region_sha256": region.region_sha256,
        "source_offset": region.offset,
        "region_length": region.length,
        "region_is_verified_code": False,
        "decoder_is_independently_validated": False,
        "analysis": result,
    }

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Inspect a manually selected candidate region in a ZDL")
    p.add_argument("zdl", type=Path)
    p.add_argument("--offset", required=True, type=lambda s: int(s, 0))
    p.add_argument("--length", required=True, type=lambda s: int(s, 0))
    p.add_argument("--sha256", default=None)
    p.add_argument("--base", type=lambda s: int(s, 0), default=0)
    args = p.parse_args(argv)
    if args.zdl.stat().st_size > 64 * 1024 * 1024:
        p.error("File exceeds 64 MiB")
    result = inspect_candidate(args.zdl.read_bytes(), args.offset, args.length,
                               args.sha256, args.base)
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
