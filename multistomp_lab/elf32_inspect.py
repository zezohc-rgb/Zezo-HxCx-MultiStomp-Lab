"""Read-only ELF32 little-endian header/section inventory for legacy ZDL.

Bounds-checks the section table. Does not relocate, link, or execute ELF.
"""
from dataclasses import dataclass, asdict
import struct
from .zdl_container import parse_zdl_container, ZDLFormatError

class ELFInspectionError(ValueError):
    pass

@dataclass(frozen=True)
class ELFSection:
    index: int
    name_offset: int
    type: int
    flags: int
    address: int
    offset: int
    size: int
    link: int
    info: int
    alignment: int
    entry_size: int

def inspect_elf32(elf: bytes) -> dict:
    if type(elf) is not bytes or len(elf) < 52:
        raise ELFInspectionError('ELF32 header truncated')
    if elf[:4] != b'\x7fELF' or elf[4] != 1 or elf[5] != 1 or elf[6] != 1:
        raise ELFInspectionError('Expected little-endian ELF32 version 1')
    (etype, machine, version, entry, phoff, shoff, flags, ehsize,
     phentsize, phnum, shentsize, shnum, shstrndx) = struct.unpack_from('<HHIIIIIHHHHHH', elf, 16)
    if version != 1 or ehsize != 52:
        raise ELFInspectionError('Unsupported ELF header version or size')
    if phnum and (phentsize < 32 or phoff > len(elf) or phnum > (len(elf)-phoff)//phentsize):
        raise ELFInspectionError('Program header table outside ELF')
    if shnum and (shentsize < 40 or shoff > len(elf) or shnum > (len(elf)-shoff)//shentsize):
        raise ELFInspectionError('Section header table outside ELF')
    if shnum and shstrndx >= shnum and shstrndx != 0xffff:
        raise ELFInspectionError('Invalid section-name table index')
    sections = []
    for i in range(shnum):
        values = struct.unpack_from('<IIIIIIIIII', elf, shoff + i * shentsize)
        section = ELFSection(i, *values)
        # SHT_NOBITS (8) occupies no bytes in the file.
        if section.type != 8 and (section.offset > len(elf) or
                                   section.size > len(elf) - section.offset):
            raise ELFInspectionError(f'Section {i} outside ELF file')
        sections.append(asdict(section))
    return {'type': etype, 'machine': machine, 'entry': entry,
            'flags': flags, 'program_header_count': phnum,
            'section_header_count': shnum, 'sections': sections,
            'instructions_executed': False}

def inspect_zdl_elf(data: bytes) -> dict:
    container = parse_zdl_container(data)
    elf = data[container.elf_offset:container.elf_offset + container.elf_size]
    return {'container': asdict(container), 'elf': inspect_elf32(elf)}
