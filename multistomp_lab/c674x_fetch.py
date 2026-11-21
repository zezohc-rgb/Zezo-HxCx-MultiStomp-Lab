"""Raw C674x 256-bit fetch-packet reader; not an instruction decoder.

This helper assumes 32-bit words and exposes raw low bits. Compact-header
packets require separate decoding and are not recognized here.
"""
from dataclasses import dataclass

class FetchPacketError(ValueError):
    pass

@dataclass(frozen=True)
class FetchPacket:
    address: int
    words: tuple[int, ...]
    p_bits: tuple[int, ...]

def read_standard_packet(data: bytes, address: int = 0) -> FetchPacket:
    if address < 0 or address % 32:
        raise FetchPacketError("fetch address must be 32-byte aligned")
    if len(data) != 32:
        raise FetchPacketError("fetch packet must be exactly 32 bytes")
    words = tuple(int.from_bytes(data[i:i + 4], "little") for i in range(0, 32, 4))
    return FetchPacket(address, words, tuple(word & 1 for word in words))

def read_packets(data: bytes, base_address: int = 0) -> list[FetchPacket]:
    if base_address < 0 or base_address % 32:
        raise FetchPacketError("base address must be 32-byte aligned")
    if len(data) % 32:
        raise FetchPacketError("input length must be a multiple of 32 bytes")
    return [read_standard_packet(data[i:i + 32], base_address + i)
            for i in range(0, len(data), 32)]
