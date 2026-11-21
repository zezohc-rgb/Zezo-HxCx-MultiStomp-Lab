"""Run an external Ziddle matcheck executable against a user-supplied ZDL.

Ziddle source: https://berbasoft.com/ziddle/ (CC0).
Build matcheck with the rig from themanro/ZoomMultistompZDL/tools/emulator.
This is an initialization test, NOT audio processing or an ASIO host.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def check_zdl(zdl: str, *, matcheck: str, knobs: int, bypass: int = 1,
              timeout: int = 60) -> subprocess.CompletedProcess[str]:
    if not 0 <= knobs <= 32:
        raise ValueError("knobs must be in range 0..32")
    if bypass not in (0, 1):
        raise ValueError("bypass must be 0 or 1")
    path = Path(zdl)
    if not path.is_file() or path.suffix.lower() != ".zdl":
        raise ValueError("An existing .ZDL file is required")
    binary = Path(matcheck)
    if not binary.is_file():
        raise ValueError("Ziddle matcheck executable not found")
    return subprocess.run(
        [str(binary.resolve()), "--params", str(knobs), "--bypass",
         str(bypass), str(path.resolve())],
        capture_output=True, text=True, timeout=timeout, check=False,
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Check ZDL init using external Ziddle matcheck")
    p.add_argument("zdl")
    p.add_argument("--matcheck", required=True, help="Path to Ziddle matcheck executable")
    p.add_argument("--knobs", type=int, required=True)
    p.add_argument("--bypass", type=int, choices=(0, 1), default=1)
    args = p.parse_args(argv)
    try:
        result = check_zdl(args.zdl, matcheck=args.matcheck,
                           knobs=args.knobs, bypass=args.bypass)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        p.exit(2, f"Ziddle test unavailable: {exc}\n")
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=__import__("sys").stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
