"""C674x standard 32-bit execute-packet boundaries.

Only packet grouping is implemented. No instruction opcode decoding or
execution occurs. Compact header-based fetch packets are explicitly rejected.
Reference: TI SPRUFE8B, sections 3.5 and 3.10.
"""
from dataclasses import dataclass
from .c674x_fetch import FetchPacket, read_packets

class UnsupportedPacket(ValueError):
    pass

@dataclass(frozen=True)
class InstructionWord:
    address: int
    raw: int
    parallel_next: bool

def is_compact_header(packet: FetchPacket) -> bool:
    # TI SPRUFE8B: header occupies eighth word; bits 31..28 are 1110.
    return (packet.words[7] >> 28) == 0xE

def group_execute_packets(data: bytes, base_address: int = 0) -> list[tuple[InstructionWord, ...]]:
    packets = read_packets(data, base_address)
    result: list[tuple[InstructionWord, ...]] = []
    current: list[InstructionWord] = []
    for packet in packets:
        if is_compact_header(packet):
            raise UnsupportedPacket(
                f"Compact-header fetch packet at 0x{packet.address:08x} is not supported"
            )
        for index, raw in enumerate(packet.words):
            current.append(InstructionWord(packet.address + 4 * index, raw, bool(raw & 1)))
            if not (raw & 1):
                result.append(tuple(current))
                current = []
            elif len(current) >= 8:
                raise UnsupportedPacket("Execute packet exceeds eight instructions")
    if current:
        raise UnsupportedPacket("Input ends during an execute packet")
    return result
