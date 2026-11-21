# ZDL research protocol

## Objective
Identify file sections, executable code, parameter storage and host dependencies
from independently obtained ZDL examples. **No layout is assumed yet.**

## Controlled comparisons
1. Obtain two legally acquired versions of the *same* effect, changing only one
   parameter or one documented modification.
2. Record provenance, file hashes and exact firmware/hardware revision.
3. Run `python -m multistomp_lab.zdl_probe effect.zdl` on each.
4. Run `python -m multistomp_lab.zdl_diff original.zdl modified.zdl`.
5. Repeat across independent examples before assigning meaning to offsets.
6. Validate any hypothesized fields with bounds checks and negative tests.
7. Separate executable DSP bytes from host metadata only when verified.

## Important limitations
- Byte differences may reflect checksums, relocation, timestamps or compression,
  not just the parameter being changed.
- The tools do not execute C674x instructions or validate ZDL headers.
- Never upload proprietary effect binaries or firmware into this repository.
- Audio fidelity must ultimately be tested against the physical MS-70CDR.
