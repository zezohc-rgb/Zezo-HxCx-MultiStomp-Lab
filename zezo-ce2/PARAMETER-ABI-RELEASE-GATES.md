# CE-2 parameter ABI and hardware release gate

Evidence: repeat98/ZoomMultistompZDL docs/EDIT-HANDLER-ABI.md and docs/STATE-ABI-PROGRESS.md (consulted 2026-11-21).

## Confirmed mapping
- First custom knob is host knob id 2, written to the float at params[5] (byte offset 20).
- Second custom knob is host knob id 3, written to params[6] (byte offset 24).
- The own-runtime zui knob handler reads a 0..255 UI value and passes it through firmware conversion before writing params[5]/params[6].
- Upstream `src/airwindows/common/zoom_params.h` explicitly documents on-pedal StereoChorus testing: the synthesized/LineSel-derived handler supplies **normalized 0..1** values; the old 0..0.14 behavior belongs to a legacy GAIN probe. Therefore the CE-2 `norm(x)` function's 0..1 branch matches the best available evidence. Its 1..100 fallback is defensive, not a claim that the handler emits percentages.
- This is **indirect** evidence: the exact CE-2 binary still needs a real-pedal control sweep.

## Release blockers
1. Record actual params[5]/params[6] at knob 0, 25, 50, 75 and 100 on a known-safe probe. Verify both controls independently.
2. Keep the evidenced 0..1 control law for the own-runtime path, and confirm CE-2's Rate and Depth sweep on hardware; do not switch to the obsolete 0..0.14 multiplier.
3. **CONFIRMED COLLISION OF OLD ID:** gid 8 / fxid 405 conflicts with themanro/ZoomMultistompZDL's Room manifest (listed in repeat98/ZoomMultistompZDL docs/FXID-REGISTRY.md, checked 2026-11-21). The manifest now uses provisional candidate **gid 8 / fxid 960**. The upstream registry `repeat98/ZoomMultistompZDL/docs/FXID-REGISTRY.md` (checked 2026-11-21) lists generated NAMLite IDs 950–957, CabIR IDs 930–945 and other gid-8 allocations but **does not list 960**. This supports a preliminary no-known-collision finding **only for that registry**, not a guarantee of global uniqueness. Verify installed IDs and other collections before any hardware release. CI uses disposable 65535 and must never publish it.
4. Confirm on real MS-70CDR that bypass, slot switching, page editing, multiple slots and audio accumulation work.
5. Compare level, rate, depth and spectral behavior against a captured Boss CE-2 reference. Host Python model is not a TI emulator.

No ZDL from the current CI should be installed on hardware.
