"""Offline C674x code-region diagnostic CLI.

Accepts a separately extracted code region, never a raw .zdl as executable
input. Reports packet inventory and CLR decoder acceptance without running it.
Decoder acceptance is NOT proof of independently verified opcode correctness.
"""
import argparse
import json
from pathlib import Path
from .c674x_trace import trace_code_region
from .c674x_clr import decode_clr_constant, DecodeError

MAX_SIZE = 64 * 1024 * 1024

def diagnose(data: bytes, base: int = 0) -> dict:
    entries = trace_code_region(data, base)
    reports = []
    supported = 0
    for entry in entries:
        item = {"address": f"0x{entry.address:08x}",
                "packet_type": entry.kind,
                "words": [f"0x{w:08x}" for w in entry.words],
                "supported": False}
        if entry.kind == "standard-execute-packet" and len(entry.words) == 1:
            try:
                decoded = decode_clr_constant(entry.words[0])
                item["instruction"] = "CLR"
                item["operands"] = {
                    "bank": decoded.side, "dst": decoded.destination,
                    "src": decoded.source, "first_bit": decoded.first_bit,
                    "last_bit": decoded.last_bit}
                item["supported"] = True
                supported += 1
            except DecodeError:
                item["reason"] = "unsupported or unknown instruction"
        else:
            item["reason"] = "compact or parallel packet not supported"
        reports.append(item)
    return {"base_address": f"0x{base:08x}",
            "packets": len(reports), "supported_packets": supported,
            "independent_opcode_validation": False,
            "executable_as_zdl": False,
            "details": reports}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code_region", type=Path)
    parser.add_argument("--base", type=lambda v: int(v, 0), default=0)
    args = parser.parse_args(argv)
    if args.code_region.suffix.lower() == ".zdl":
        parser.error("Raw ZDL input is not supported: extract and verify code region first")
    if args.code_region.stat().st_size > MAX_SIZE:
        parser.error("Code region exceeds 64 MiB")
    print(json.dumps(diagnose(args.code_region.read_bytes(), args.base), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
