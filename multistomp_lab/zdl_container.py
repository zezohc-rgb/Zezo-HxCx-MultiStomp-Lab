"""Strict read-only parser for original Zoom MultiStomp ZDL containers.

Layout independently documented by repeat98/ZoomMultistompZDL, build/zdl.py.
This is a fresh minimal metadata-only implementation. No ELF execution.
"""
from dataclasses import dataclass
import hashlib
import struct

MAX_ZDL_SIZE = 64 * 1024 * 1024
INFO_END = 76

class ZDLFormatError(ValueError):
    pass

@dataclass(frozen=True)
class ZDLContainer:
    elf_offset: int
    elf_size: int
    header_size: int
    extra_header_size: int
    category: int
    effect_version: str
    elf_sha256: str
    declared_elf_size_matches_file: bool

def parse_zdl_container(data: bytes) -> ZDLContainer:
    if type(data) is not bytes or not INFO_END <= len(data) <= MAX_ZDL_SIZE:
        raise ZDLFormatError('Invalid ZDL input or size')
    if data[:8] != bytes(4) + b'SIZE' or data[20:24] != b'INFO':
        raise ZDLFormatError('Not a legacy ZDL SIZE/INFO container')
    size_payload, header_size, elf_size = struct.unpack_from('<III', data, 8)
    info_size = struct.unpack_from('<I', data, 24)[0]
    if size_payload != 8 or info_size != 48:
        raise ZDLFormatError('Unexpected SIZE/INFO block sizes')
    elf_offset = 20 + header_size
    if elf_offset < INFO_END or elf_offset > len(data):
        raise ZDLFormatError('Invalid ELF offset')
    if elf_size < 4 or elf_size > len(data) - elf_offset:
        raise ZDLFormatError('ELF payload exceeds file bounds')
    elf = data[elf_offset:elf_offset + elf_size]
    if elf[:4] != b'\x7fELF':
        raise ZDLFormatError('Missing ELF magic at declared offset')
    if len(elf) < 16 or elf[4] != 1 or elf[5] != 1:
        raise ZDLFormatError('Expected 32-bit little-endian ELF identification')
    version = data[68:76].split(b'\x00', 1)[0].decode('ascii', 'replace')
    return ZDLContainer(
        elf_offset=elf_offset, elf_size=elf_size, header_size=header_size,
        extra_header_size=elf_offset - INFO_END, category=data[60],
        effect_version=version, elf_sha256=hashlib.sha256(elf).hexdigest(),
        declared_elf_size_matches_file=(elf_offset + elf_size == len(data)),
    )
