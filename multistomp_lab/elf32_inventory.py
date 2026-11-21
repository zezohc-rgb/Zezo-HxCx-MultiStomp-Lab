"""Classify executable ELF32 sections and inventory relocation tables.

Read-only; does not resolve TI C6000-specific relocation types or load code.
"""
from .elf32_inspect import inspect_elf32, ELFInspectionError

SHF_EXECINSTR = 4
SHT_REL = 9
SHT_RELA = 4
SHT_SYMTAB = 2
SHT_DYNSYM = 11

def inventory_elf32(elf: bytes) -> dict:
    metadata = inspect_elf32(elf)
    sections = metadata['sections']
    executable = []
    relocations = []
    symbols = []
    for section in sections:
        kind = section['type']
        if section['flags'] & SHF_EXECINSTR:
            if kind == 8:
                raise ELFInspectionError('Executable section cannot be NOBITS for extraction')
            executable.append({
                'index': section['index'], 'file_offset': section['offset'],
                'virtual_address': section['address'], 'size': section['size'],
                'aligned_to_32_bytes': section['offset'] % 32 == 0 and section['size'] % 32 == 0,
            })
        if kind in (SHT_REL, SHT_RELA, SHT_SYMTAB, SHT_DYNSYM):
            if section['link'] >= len(sections):
                raise ELFInspectionError('Linked section index outside section table')
            if kind in (SHT_REL, SHT_RELA) and section['info'] >= len(sections):
                raise ELFInspectionError('Relocation target outside section table')
            if kind in (SHT_REL, SHT_RELA):
                minimum = 8 if kind == SHT_REL else 12
                if section['entry_size'] < minimum or section['size'] % section['entry_size']:
                    raise ELFInspectionError('Invalid relocation entry size')
                relocations.append({
                    'index': section['index'], 'type': 'REL' if kind == SHT_REL else 'RELA',
                    'entries': section['size'] // section['entry_size'],
                    'symbol_table_section': section['link'],
                    'target_section': section['info'],
                })
            else:
                if section['entry_size'] < 16 or section['size'] % section['entry_size']:
                    raise ELFInspectionError('Invalid symbol entry size')
                symbols.append({
                    'index': section['index'], 'entries': section['size'] // section['entry_size'],
                    'string_table_section': section['link'],
                })
    return {'elf_machine': metadata['machine'], 'executable_sections': executable,
            'relocation_tables': relocations, 'symbol_tables': symbols,
            'relocations_applied': False, 'instructions_executed': False}
