# C674x decode implementation plan

Primary reference: TI SPRUFE8B, *TMS320C674x DSP CPU and Instruction Set User's Guide*:
https://www.ti.com/lit/ug/sprufe8b/sprufe8b.pdf

## Implemented
- Read aligned 256-bit fetch packets as eight little-endian 32-bit words.
- Expose raw low bits for subsequent standard-instruction parallelism analysis.
- Unit tests for alignment, length and byte order.

## Not implemented
- Detecting and decoding compact 16-bit header-based packets.
- Distinguishing valid opcodes from arbitrary bytes.
- Predication, execution packets, parallel issue, pipeline delays and branches.
- C674x arithmetic and floating-point semantics.
- Actual ZDL executable section identification and host services.

## Next validation gate
Build instruction fixtures from documented TI encodings or a legal assembler,
check expected disassembly against independent reference, then implement a
small opcode subset with exact flags and register semantics. Do not assume
that every 32-byte slice of a ZDL is executable code.
