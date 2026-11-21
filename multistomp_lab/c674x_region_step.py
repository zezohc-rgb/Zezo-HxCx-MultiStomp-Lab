"""Strict execution of verified, aligned code regions containing serial CLR only.

This bridge combines the fetch/execute-packet tracer with the narrow CLR
decoder. It rejects compact packets, parallel packets and unknown opcodes
before any register mutation. NOT a general C674x or ZDL emulator.
"""
from dataclasses import dataclass, field
from .c674x_trace import trace_code_region
from .c674x_clr import decode_clr_constant, execute_clr_constant
from .c674x_state import RegisterFile


class UnsupportedCodeRegion(ValueError):
    pass


@dataclass
class RegionStepper:
    registers: RegisterFile = field(default_factory=RegisterFile)
    retired: int = 0

    def execute(self, code: bytes, base_address: int = 0) -> tuple[int, ...]:
        trace = trace_code_region(code, base_address)
        decoded = []
        for entry in trace:
            if entry.kind != 'standard-execute-packet' or len(entry.words) != 1:
                raise UnsupportedCodeRegion(
                    f'Unsupported packet at 0x{entry.address:08x}: {entry.kind}, '
                    f'{len(entry.words)} words'
                )
            decoded.append(decode_clr_constant(entry.words[0]))
        # All instructions validated before execution; decoding errors do not
        # partially modify the register file.
        values = tuple(execute_clr_constant(self.registers, op) for op in decoded)
        self.retired += len(values)
        return values
