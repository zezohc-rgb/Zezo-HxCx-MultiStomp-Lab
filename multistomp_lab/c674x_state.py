"""C674x integer register-bank state and a deliberately limited semantic harness.

This is NOT a binary instruction decoder or a cycle-accurate CPU.
Operations are explicit test operations, never inferred from ZDL bytes.
"""
from dataclasses import dataclass, field

MASK32 = (1 << 32) - 1

class UnsupportedOperation(ValueError):
    pass

@dataclass
class RegisterFile:
    a: list[int] = field(default_factory=lambda: [0] * 32)
    b: list[int] = field(default_factory=lambda: [0] * 32)

    def _bank(self, side: str) -> list[int]:
        if side == 'A':
            return self.a
        if side == 'B':
            return self.b
        raise ValueError('Register bank must be A or B')

    def read(self, side: str, index: int) -> int:
        bank = self._bank(side)
        if type(index) is not int or not 0 <= index < 32:
            raise ValueError('Register index out of range')
        return bank[index]

    def write(self, side: str, index: int, value: int) -> None:
        bank = self._bank(side)
        if type(index) is not int or not 0 <= index < 32 or type(value) is not int:
            raise ValueError('Invalid register write')
        bank[index] = value & MASK32

@dataclass(frozen=True)
class TestOperation:
    mnemonic: str
    dst: tuple[str, int]
    src1: tuple[str, int] | None = None
    src2: tuple[str, int] | None = None
    immediate: int | None = None


def execute_test_operation(registers: RegisterFile, operation: TestOperation) -> int:
    """Execute a hand-authored test IR, not decoded C674x machine code."""
    name = operation.mnemonic.upper()
    if name == 'MVK':
        if operation.immediate is None or operation.src1 is not None or operation.src2 is not None:
            raise UnsupportedOperation('MVK requires only an immediate')
        value = operation.immediate & MASK32
    elif name in ('ADD', 'SUB', 'AND', 'OR', 'XOR'):
        if operation.src1 is None or operation.src2 is None or operation.immediate is not None:
            raise UnsupportedOperation(f'{name} requires two register operands')
        left = registers.read(*operation.src1)
        right = registers.read(*operation.src2)
        value = {'ADD': lambda: left + right, 'SUB': lambda: left - right,
                 'AND': lambda: left & right, 'OR': lambda: left | right,
                 'XOR': lambda: left ^ right}[name]() & MASK32
    else:
        raise UnsupportedOperation(f'Unsupported test operation: {operation.mnemonic}')
    registers.write(*operation.dst, value)
    return value
