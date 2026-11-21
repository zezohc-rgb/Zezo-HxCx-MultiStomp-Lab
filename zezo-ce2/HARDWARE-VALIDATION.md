# Zezo CE-2 — hardware validation gates

**EXPERIMENTAL: no installable ZDL is released.** Compilation is not proof of pedal safety.

## Before testing
1. Back up existing patches/effects and verify the backup is readable.
2. Verify MS-70CDR model/firmware and ensure gid 8 / fxid 960 is not installed.
3. Establish a working recovery plan. If recovery is unavailable, do not flash: an incompatible ZDL may freeze the pedal and require hardware repair.
4. Never install CI diagnostic ID 65535. The CI publishes metadata only.

## Staged acceptance
| Stage | Required check |
|---|---|
| 0 | Bypass-only: boots, toggles, edits, changes slots, survives power cycle |
| 1 | State initialization: repeat loads/unloads without freezes |
| 2 | Audio: both channels, no silence, glitches, excessive gain or noise |
| Controls | Rate and Depth at 0/25/50/75/100; independent smooth changes |
| Slots | Multiple effects, patch switching, six-slot interaction, power cycle |
| Sound | Level-matched recording against Boss CE-2 reference, spectrum/modulation comparison |

Stop immediately if a stage fails. Do not infer that any gate passed without a real pedal result.

## Current evidence
- Upstream edit-handler ABI maps Rate to params[5] and Depth to params[6].
- Upstream StereoChorus hardware tests support normalized 0..1 control values; Zezo CE-2 remains unmeasured.
- TI C6000 build and structural ZDL packaging passed in CI run #94.
- FXID 960 is absent from the reviewed upstream registry but is not globally guaranteed unique.
- The DSP is CE-2-inspired, not a verified circuit-accurate Boss CE-2 reproduction.
