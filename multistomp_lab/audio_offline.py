"""Deterministic PCM16 WAV processing harness for the future ZDL runtime.

This module does NOT emulate C674x, decode DSP instructions, or apply effects.
It establishes a verifiable stereo audio boundary for a future DSP backend.
"""
from __future__ import annotations

import argparse
import wave
from pathlib import Path


class BackendUnavailable(RuntimeError):
    """No real ZDL execution backend is connected."""


def process_wav(input_path: str, output_path: str, *, effect_slots: int = 0) -> dict:
    """Copy uncompressed PCM16 mono/stereo WAV with no gain or sample alteration.

    Refuse any nonzero effect count: never imply that bypass means processing.
    """
    if effect_slots != 0:
        raise BackendUnavailable(
            "Cannot process ZDL slots: C674x execution backend is not implemented"
        )
    src = Path(input_path)
    dst = Path(output_path)
    if src.resolve() == dst.resolve():
        raise ValueError("Input and output must be different files")
    with wave.open(str(src), "rb") as reader:
        if reader.getcomptype() != "NONE" or reader.getsampwidth() != 2:
            raise ValueError("Only uncompressed 16-bit PCM WAV is supported")
        if reader.getnchannels() not in (1, 2):
            raise ValueError("Only mono and stereo WAV are supported")
        params = reader.getparams()
        with wave.open(str(dst), "wb") as writer:
            writer.setparams(params)
            while True:
                frames = reader.readframes(4096)
                if not frames:
                    break
                writer.writeframesraw(frames)
    return {"sample_rate": params.framerate, "channels": params.nchannels,
            "frames": params.nframes, "processed_effects": 0,
            "status": "bit_exact_pcm_bypass_only"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PCM16 WAV bypass test, NOT ZDL audio")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--slots", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        print(process_wav(args.input, args.output, effect_slots=args.slots))
    except (OSError, ValueError, BackendUnavailable, wave.Error) as exc:
        parser.exit(2, f"Audio test failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
