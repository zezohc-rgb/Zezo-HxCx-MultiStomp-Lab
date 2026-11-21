"""Bounded little-endian DSP memory map; not yet a C674x interpreter."""
from dataclasses import dataclass

class MemoryFault(Exception):
    pass

@dataclass(frozen=True)
class Region:
    start: int
    size: int
    writable: bool = True

    def __post_init__(self):
        if not (0 <= self.start < 2**32 and 0 < self.size <= 2**32 - self.start):
            raise ValueError("Invalid 32-bit region")

class DSPMemory:
    def __init__(self):
        self._regions = []

    def map_region(self, region: Region, initial: bytes = b""):
        if len(initial) > region.size or region.size > 64 * 1024 * 1024:
            raise ValueError("Region too large or initializer does not fit")
        for other, _ in self._regions:
            if region.start < other.start + other.size and other.start < region.start + region.size:
                raise ValueError("Overlapping regions")
        self._regions.append((region, bytearray(initial.ljust(region.size, b"\x00"))))

    def _locate(self, address: int, size: int, write: bool = False):
        if not isinstance(address, int) or not isinstance(size, int) or size <= 0 or address < 0 or address + size > 2**32:
            raise MemoryFault("Invalid address or size")
        for region, data in self._regions:
            if region.start <= address and address + size <= region.start + region.size:
                if write and not region.writable:
                    raise MemoryFault("Write to read-only memory")
                return data, address - region.start
        raise MemoryFault("Unmapped address")

    def read(self, address: int, size: int) -> bytes:
        data, offset = self._locate(address, size)
        return bytes(data[offset:offset + size])

    def write(self, address: int, payload: bytes):
        data, offset = self._locate(address, len(payload), True)
        data[offset:offset + len(payload)] = payload

    def read_u32(self, address: int) -> int:
        if address % 4:
            raise MemoryFault("Unaligned read")
        return int.from_bytes(self.read(address, 4), "little")

    def write_u32(self, address: int, value: int):
        if address % 4 or not isinstance(value, int) or not 0 <= value < 2**32:
            raise MemoryFault("Invalid 32-bit store")
        self.write(address, value.to_bytes(4, "little"))
