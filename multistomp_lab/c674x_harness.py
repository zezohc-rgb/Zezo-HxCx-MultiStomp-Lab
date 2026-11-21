"""Test-only state machine linking register operations to mapped DSP memory.

Not a C674x instruction decoder, CPU pipeline, or ZDL runner. Operations
are explicit intermediate representations supplied by tests.
"""
from dataclasses import dataclass, field
from .c674x_state import RegisterFile, TestOperation, execute_test_operation
from .dsp_memory import DSPMemory

@dataclass(frozen=True)
class MemoryOperation:
    mnemonic: str
    register: tuple[str, int]
    address: int

@dataclass
class TestMachine:
    registers: RegisterFile = field(default_factory=RegisterFile)
    memory: DSPMemory = field(default_factory=DSPMemory)
    steps: int = 0

    def step(self, operation: TestOperation | MemoryOperation) -> int:
        if isinstance(operation, TestOperation):
            result = execute_test_operation(self.registers, operation)
        elif isinstance(operation, MemoryOperation):
            if operation.mnemonic == 'LDW':
                value = self.memory.read_u32(operation.address)
                self.registers.write(*operation.register, value)
                result = value
            elif operation.mnemonic == 'STW':
                value = self.registers.read(*operation.register)
                self.memory.write_u32(operation.address, value)
                result = value
            else:
                raise ValueError('Unsupported test memory operation')
        else:
            raise TypeError('Expected a test operation')
        self.steps += 1
        return result
