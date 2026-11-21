"""Narrow 32-bit C674x CLR constant-form decoder.

Only unconditional, nonparallel CLR .S1/.S2 with constant bit positions is
accepted. All other opcodes/conditions are rejected rather than guessed.
Reference: TI SPRUFE8B, CLR — Clear a Bit Field, constant-form encoding.
"""
from dataclasses import dataclass
from .c674x_state import RegisterFile


class DecodeError(ValueError):
    pass


@dataclass(frozen=True)
class ClearField:
    side: str
    destination: int
    source: int
    first_bit: int
    last_bit: int


def decode_clr_constant(word: int) -> ClearField:
    if type(word) is not int or not 0 <= word <= 0xffffffff:
        raise DecodeError('Expected an unsigned 32-bit instruction word')
    # Fixed bits [7:2] are 110010, according to the TI CLR table.
    if ((word >> 2) & 0x3f) != 0b110010:
        raise DecodeError('Not CLR constant form')
    # This first decoder handles only unconditional and nonparallel operations.
    if (word >> 28) != 0 or (word & 1):
        raise DecodeError('Conditional or parallel CLR is not yet supported')
    side = 'B' if (word >> 1) & 1 else 'A'
    return ClearField(side, (word >> 23) & 31, (word >> 18) & 31,
                      (word >> 13) & 31, (word >> 8) & 31)


def execute_clr_constant(registers: RegisterFile, instruction: ClearField) -> int:
    value = registers.read(instruction.side, instruction.source)
    lo, hi = instruction.first_bit, instruction.last_bit
    if lo <= hi:
        mask = ((1 << (hi - lo + 1)) - 1) << lo
        value &= ~mask & 0xffffffff
    registers.write(instruction.side, instruction.destination, value)
    return value
