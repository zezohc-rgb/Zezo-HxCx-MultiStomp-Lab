# CE-2 parameter ABI and hardware release gate

Evidence: repeat98/ZoomMultistompZDL docs/EDIT-HANDLER-ABI.md and docs/STATE-ABI-PROGRESS.md (consulted 2026-11-21).

## Confirmed mapping
- First custom knob is host knob id 2, written to the float at params[5] (byte offset 20).
- Second custom knob is host knob id 3, written to params[6] (byte offset 24).
- Host callback uses a 0..255 raw knob representation and a LineSel-derived edit handler; a fixed float scale of 0..1 **is not established**.
- Hardware observations for a different effect report raw values as small as 0..0.14 before effect-specific scaling.

## Release blockers
1. Record actual params[5]/params[6] at knob 0, 25, 50, 75 and 100 on a known-safe probe. Verify both controls independently.
2. Select the scaling law only after measurement; current norm(x) is provisional and treats 0..1 differently from 1..100.
3. **CONFIRMED COLLISION:** current provisional gid 8 / fxid 405 conflicts with themanro/ZoomMultistompZDL's Room manifest (listed in repeat98/ZoomMultistompZDL docs/FXID-REGISTRY.md, section IDs used by other collections, checked 2026-11-21). NEVER install or release this ID. Select a new identifier only after checking all known collections and the pedal's existing effects. CI uses disposable 65535 and must never publish it.
4. Confirm on real MS-70CDR that bypass, slot switching, page editing, multiple slots and audio accumulation work.
5. Compare level, rate, depth and spectral behavior against a captured Boss CE-2 reference. Host Python model is not a TI emulator.

No ZDL from the current CI should be installed on hardware.
