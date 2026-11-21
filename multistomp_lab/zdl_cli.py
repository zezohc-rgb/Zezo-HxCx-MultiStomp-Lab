"""Command-line read-only inspection of legacy Zoom MultiStomp ZDL files.

Usage: python -m multistomp_lab.zdl_cli path/to/effect.zdl
No DSP execution, audio output, or proprietary file redistribution.
"""
import argparse
import json
import sys
from pathlib import Path
from dataclasses import asdict
from .zdl_container import parse_zdl_container, ZDLFormatError, MAX_ZDL_SIZE
from .elf32_inspect import inspect_elf32, ELFInspectionError
from .elf32_inventory import inventory_elf32
from .elf32_load_plan import plan_elf32_sections

def inspect_file(path: str) -> dict:
    file = Path(path)
    if file.stat().st_size > MAX_ZDL_SIZE:
        raise ZDLFormatError('ZDL file exceeds maximum supported size')
    data = file.read_bytes()
    container = parse_zdl_container(data)
    elf = data[container.elf_offset:container.elf_offset + container.elf_size]
    return {
        'file_name': file.name,
        'container': asdict(container),
        'elf_header': inspect_elf32(elf),
        'inventory': inventory_elf32(elf),
        'load_plan': plan_elf32_sections(elf),
        'runtime_status': 'inspection_only_not_executable',
    }

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Inspect a legacy MS-70CDR ZDL (read-only)')
    parser.add_argument('zdl', help='Path to .zdl file')
    parser.add_argument('--output', help='Optional JSON output path')
    args = parser.parse_args(argv)
    try:
        result = inspect_file(args.zdl)
        report = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(report + '\n', encoding='utf-8')
        else:
            print(report)
        return 0
    except (OSError, ZDLFormatError, ELFInspectionError, ValueError) as exc:
        print(f'ZDL inspection failed: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
