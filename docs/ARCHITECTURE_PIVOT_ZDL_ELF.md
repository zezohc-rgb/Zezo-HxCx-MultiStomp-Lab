# Architecture pivot: verified ZDL/ELF loader and Ziddle evaluation

2026-11-21. This supersedes the previous assumption that ZDL section locations
must be inferred using entropy or arbitrary offsets.

## Independent public references

- https://github.com/repeat98/ZoomMultistompZDL
- https://github.com/repeat98/ZoomMultistompZDL/blob/main/docs/ZDL-REVERSE-ENGINEERING-STATUS.md
- https://github.com/repeat98/ZoomMultistompZDL/blob/main/docs/OBTAINING-REFERENCE-FILES.md
- https://github.com/themanro/ZoomMultistompZDL/blob/main/docs/EMULATOR-TESTING.md
- https://github.com/themanro/ZoomMultistompZDL/blob/main/build/disassemble_zdl.py
- https://www.ti.com/lit/ug/sprui04/sprui04.pdf (verify current official document revision)

The documented original MS-70CDR ZDL format wraps a TI C6000 ELF.
The separate ZD2 family also uses a ZDLF container; do not confuse the two.

## Immediate implementation gates

1. Obtain legally distributed custom test ZDL, inspect magic, embedded ELF,
   section headers, symbols, relocations, and executable segment offsets using
   established tools. Never commit Zoom proprietary stock binaries.
2. Compare our candidate extractor and synthetic CLR opcode assumptions against
   actual disassembler/assembler output. Synthetic self-consistency is insufficient.
3. Evaluate Ziddle's current source, license, Windows build path, supported
   peripherals, audio callback and host ABI; decide whether to integrate it
   rather than write a new C674x core.
4. Build one headless effect runner that can initialize and process a known
   open-source ZDL on deterministic audio frames; compare outputs to a trusted
   baseline, including stereo, bypass, parameters and sample-rate changes.
5. Only then implement six-slot routing, resource accounting, ASIO streaming,
   GUI and installer.

## Current limitations

Our C674x CLR decoder has NOT been validated with an independent machine-code
fixture. The packet tracer and manual region selection do not prove ZDL code
execution. The project has no functional audio engine or ZDL loader. Existing
diagnostic modules remain useful as exploratory tools, not a production runtime.

## Licensing and provenance

Check Ziddle and each upstream project's license before vendoring code.
Retain upstream attribution and distinguish code from technical findings.
Do not redistribute Zoom firmware or stock ZDLs without authorization.
