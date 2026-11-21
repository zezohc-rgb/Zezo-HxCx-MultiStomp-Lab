"""Fail-closed single-instruction C674x CLR stepper.

Only nonpredicated, nonparallel 32-bit CLR constant form is supported.
No cycle timing, compact opcodes, memory instructions or ZDL loading.
"""
from dataclasses import dataclass, field
from .c674x_clr import decode_clr_constant, execute_clr_constant, DecodeError
from .c674x_state import RegisterFile

@dataclass
class CLRStepper:
    registers: RegisterFile = field(default_factory=RegisterFile)
    instructions_retired: int = 0

    def step_word(self, word: int) -> int:
        decoded = decode_clr_constant(word)
        value = execute_clr_constant(self.registers, decoded)
        self.instructions_retired += 1
        return value

    def step_bytes(self, code: bytes) -> list[int]:
        """Execute independent serial CLR words; reject all other words.

        Validate the entire stream before modifying registers to prevent
        partially executing an unsupported stream.
        """
        if len(code) % 4:
            raise DecodeError('Instruction stream must be 32-bit aligned')
        words = [int.from_bytes(code[i:i+4], 'little') for i in range(0, len(code), 4)]
        for word in words:
            decode_clr_constant(word)
        return [self.step_word(word) for word in words]
