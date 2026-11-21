"""Generate a deterministic 44.1 kHz stereo WAV and compare Ziddle output.

Usage:
  python tools/ziddle_audio_probe.py make input.wav
  ziddle effect render EFFECT.ZDL input.wav output.wav --firmware UPDATER.zip
  python tools/ziddle_audio_probe.py compare input.wav output.wav

The comparison is evidence of changed audio, not proof of correct DSP.
"""
import argparse
import math
import struct
import wave
from pathlib import Path


def read_pcm(path):
    with wave.open(str(path), "rb") as wav:
        if wav.getcomptype() != "NONE" or wav.getsampwidth() != 2:
            raise ValueError("Expected uncompressed PCM16 WAV")
        info = (wav.getnchannels(), wav.getframerate(), wav.getnframes())
        raw = wav.readframes(wav.getnframes())
    if len(raw) % 2:
        raise ValueError("Invalid PCM byte count")
    return info, struct.unpack("<" + "h" * (len(raw) // 2), raw)


def make(path):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        samples = []
        for i in range(44100):
            tone = math.sin(2 * math.pi * 220 * i / 44100)
            envelope = math.exp(-i / 12000)
            sample = round(12000 * tone * envelope)
            samples.extend((sample, sample))
        wav.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    print("Generated 44.1 kHz stereo PCM16 test tone:", path)


def compare(source, rendered):
    source_info, a = read_pcm(source)
    output_info, b = read_pcm(rendered)
    if source_info != output_info:
        raise ValueError(f"Format or duration mismatch: {source_info} != {output_info}")
    differences = sum(x != y for x, y in zip(a, b))
    peak = max((abs(x) for x in b), default=0)
    rms = math.sqrt(sum(x * x for x in b) / len(b)) if b else 0
    print(f"Compared {len(a)} samples; changed={differences}; output_peak={peak}; output_rms={rms:.2f}")
    if differences == 0:
        raise ValueError("No changed samples; effect may be bypassed or neutral")
    if peak == 0:
        raise ValueError("Output is silent")
    print("Audio changed. This does NOT establish correct ZDL emulation.")


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("make").add_argument("output", type=Path)
    cmp = commands.add_parser("compare")
    cmp.add_argument("input", type=Path)
    cmp.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "make":
        make(args.output)
    else:
        compare(args.input, args.output)


if __name__ == "__main__":
    main()
