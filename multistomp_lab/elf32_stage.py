"""Materialize ELF32 SHF_ALLOC sections into isolated read-only memory images.

This is staging only, NOT relocation, linking, DSP execution or audio processing.
"""
from dataclasses import dataclass
from .elf32_load_plan import plan_elf32_sections
from .elf32_inspect import ELFInspectionError

@dataclass(frozen=True)
class MemoryImage:
    address: int
    data: bytes
    writable: bool
    executable: bool

def stage_elf32(elf: bytes) -> tuple[MemoryImage, ...]:
    plan = plan_elf32_sections(elf)
    images = []
    for section in plan['sections']:
        size = section['size']
        if section['zero_fill']:
            payload = bytes(size)
        else:
            offset = section['source_offset']
            if offset is None or offset > len(elf) or size > len(elf) - offset:
                raise ELFInspectionError('Section payload outside ELF')
            payload = elf[offset:offset + size]
        images.append(MemoryImage(
            address=section['virtual_address'], data=payload,
            writable=section['writable'], executable=section['executable'],
        ))
    return tuple(images)

def read_staged(images: tuple[MemoryImage, ...], address: int, size: int) -> bytes:
    if address < 0 or size < 0 or address + size > 2**32:
        raise ELFInspectionError('Invalid DSP memory range')
    for image in images:
        if image.address <= address and address + size <= image.address + len(image.data):
            start = address - image.address
            return image.data[start:start + size]
    raise ELFInspectionError('DSP address not mapped to one staged section')
