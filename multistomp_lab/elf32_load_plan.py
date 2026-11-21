"""Build a non-executable ELF32 section load plan.

This is NOT a DSP loader: no relocations are applied and no memory is mutated.
Uses SHF_ALLOC and SHT_NOBITS according to TI C6000 EABI (SPRAB89B).
"""
from dataclasses import dataclass, asdict
from .elf32_inspect import inspect_elf32, ELFInspectionError

SHF_WRITE = 0x1
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
SHT_NOBITS = 8
MAX_ALLOCATED = 64 * 1024 * 1024

@dataclass(frozen=True)
class PlannedSection:
    index: int
    virtual_address: int
    size: int
    source_offset: int | None
    writable: bool
    executable: bool
    zero_fill: bool

def plan_elf32_sections(elf: bytes) -> dict:
    info = inspect_elf32(elf)
    sections = []
    ranges = []
    total = 0
    for s in info['sections']:
        if not s['flags'] & SHF_ALLOC or not s['size']:
            continue
        start, size = s['address'], s['size']
        if size > 2**32 - start:
            raise ELFInspectionError('Section extends beyond 32-bit DSP address space')
        alignment = s['alignment']
        if alignment not in (0, 1) and (
            alignment & (alignment - 1) or start % alignment
        ):
            raise ELFInspectionError('Invalid section address alignment')
        end = start + size
        if any(start < other_end and other_start < end
               for other_start, other_end in ranges):
            raise ELFInspectionError('Overlapping allocated section addresses')
        if s['type'] == SHT_NOBITS and s['flags'] & SHF_EXECINSTR:
            raise ELFInspectionError('Executable NOBITS section is unsupported')
        total += size
        if total > MAX_ALLOCATED:
            raise ELFInspectionError('Allocated sections exceed 64 MiB')
        ranges.append((start, end))
        sections.append(asdict(PlannedSection(
            index=s['index'], virtual_address=start, size=size,
            source_offset=None if s['type'] == SHT_NOBITS else s['offset'],
            writable=bool(s['flags'] & SHF_WRITE),
            executable=bool(s['flags'] & SHF_EXECINSTR),
            zero_fill=s['type'] == SHT_NOBITS,
        )))
    return {
        'elf_machine': info['machine'],
        'sections': sections,
        'total_allocated_bytes': total,
        'relocations_applied': False,
        'memory_mutated': False,
        'code_executed': False,
    }
