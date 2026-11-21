"""Atomic execute-packet harness for manually authored test operations.

C674x execute packets issue instructions together. This model reads all source
registers from a snapshot, then commits writes together. It is NOT an opcode
decoder, functional-unit scheduler, latency model, or hardware-accurate emulator.
"""
from dataclasses import dataclass
from .c674x_state import RegisterFile, TestOperation, MASK32, UnsupportedOperation

class PacketConflict(ValueError):
    pass

@dataclass(frozen=True)
class PacketResult:
    writes: tuple[tuple[str, int, int], ...]

def evaluate_packet(registers: RegisterFile, operations: tuple[TestOperation, ...]) -> PacketResult:
    if not 1 <= len(operations) <= 8:
        raise PacketConflict("An execute packet requires 1..8 operations")
    snapshot = RegisterFile(registers.a.copy(), registers.b.copy())
    writes = []
    targets = set()
    for op in operations:
        if not isinstance(op, TestOperation):
            raise TypeError("Only manually authored test operations are supported")
        side, index = op.dst
        # Validate target without modifying the live register file.
        snapshot.read(side, index)
        if op.dst in targets:
            raise PacketConflict("Multiple writes to the same register")
        targets.add(op.dst)
        name = op.mnemonic.upper()
        if name == "MVK":
            if op.immediate is None or op.src1 is not None or op.src2 is not None:
                raise UnsupportedOperation("MVK requires an immediate")
            value = op.immediate & MASK32
        elif name in ("ADD", "SUB", "AND", "OR", "XOR"):
            if op.src1 is None or op.src2 is None or op.immediate is not None:
                raise UnsupportedOperation("Two register sources required")
            a = snapshot.read(*op.src1)
            b = snapshot.read(*op.src2)
            if name == "ADD": value = a + b
            elif name == "SUB": value = a - b
            elif name == "AND": value = a & b
            elif name == "OR": value = a | b
            else: value = a ^ b
            value &= MASK32
        else:
            raise UnsupportedOperation(name)
        writes.append((side, index, value))
    return PacketResult(tuple(writes))

def commit_packet(registers: RegisterFile, result: PacketResult) -> None:
    for side, index, value in result.writes:
        registers.write(side, index, value)

def execute_packet(registers: RegisterFile, operations: tuple[TestOperation, ...]) -> PacketResult:
    result = evaluate_packet(registers, operations)
    commit_packet(registers, result)
    return result
