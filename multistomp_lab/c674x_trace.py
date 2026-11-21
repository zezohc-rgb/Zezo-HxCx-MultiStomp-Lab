"""Conservative fetch-packet trace, without claiming opcode decoding.

Consumes an independently identified, aligned code region. Standard 32-bit
words expose P-bit boundaries. Compact headers are recorded but deliberately
not interpreted as executable instruction packets.
"""
from dataclasses import dataclass
from .c674x_scan import scan_code_region


@dataclass(frozen=True)
class TraceEntry:
    address: int
    kind: str
    words: tuple[int, ...]


class TraceError(ValueError):
    pass


def trace_code_region(data: bytes, base_address: int = 0) -> list[TraceEntry]:
    packets = scan_code_region(data, base_address)
    entries: list[TraceEntry] = []
    pending: list[int] = []
    start: int | None = None
    for packet in packets:
        if packet.kind != 'standard':
            if pending:
                raise TraceError('Compact header encountered during unfinished standard execute packet')
            entries.append(TraceEntry(packet.address, 'compact-opaque', packet.raw_words))
            continue
        for index, word in enumerate(packet.raw_words):
            if start is None:
                start = packet.address + index * 4
            pending.append(word)
            if len(pending) > 8:
                raise TraceError('Execute packet exceeds eight 32-bit instructions')
            if word & 1 == 0:
                entries.append(TraceEntry(start, 'standard-execute-packet', tuple(pending)))
                pending.clear()
                start = None
    if pending:
        raise TraceError('Code region ends during unfinished execute packet')
    return entries
