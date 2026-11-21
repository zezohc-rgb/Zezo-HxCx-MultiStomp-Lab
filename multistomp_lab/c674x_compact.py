"""C674x compact fetch-packet header inspection, not opcode decoding.

TI SPRUFE8B section 3.10.2: word 7 contains 1110, layout, expansion,
and 14 p bits. Compact words contain two 16-bit instructions.
"""
from dataclasses import dataclass

class CompactHeaderError(ValueError):
    pass

@dataclass(frozen=True)
class CompactHeader:
    raw: int
    layout: int
    expansion: int
    parallel_bits: int

    @property
    def compact_words(self) -> tuple[bool, ...]:
        return tuple(bool(self.layout & (1 << i)) for i in range(7))

def parse_compact_header(word: int) -> CompactHeader:
    if not isinstance(word, int) or not 0 <= word <= 0xFFFFFFFF:
        raise CompactHeaderError("Header must be an unsigned 32-bit word")
    if word >> 28 != 0xE:
        raise CompactHeaderError("Not a compact fetch-packet header")
    return CompactHeader(word, (word >> 21) & 0x7F,
                         (word >> 14) & 0x7F, word & 0x3FFF)

def inspect_compact_fetch_packet(data: bytes) -> dict:
    if len(data) != 32:
        raise CompactHeaderError("Fetch packet must contain 32 bytes")
    words = tuple(int.from_bytes(data[i:i + 4], "little") for i in range(0, 32, 4))
    header = parse_compact_header(words[7])
    entries = []
    for i, is_compact in enumerate(header.compact_words):
        if is_compact:
            entries.append({"word": i, "width": 16, "raw": [words[i] & 0xFFFF, words[i] >> 16]})
        else:
            entries.append({"word": i, "width": 32, "raw": [words[i]]})
    return {"layout": header.layout, "expansion": header.expansion,
            "parallel_bits": header.parallel_bits, "instructions": entries,
            "decoded": False, "executable": False}
