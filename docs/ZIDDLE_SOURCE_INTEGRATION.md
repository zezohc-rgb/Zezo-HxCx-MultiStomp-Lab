# Ziddle source acquisition and integration status

Official page: https://berbasoft.com/ziddle/
Source ZIP advertised on 2026-11-21:
https://berbasoft.com/ziddle/ziddle-1794645921.zip

The site describes Ziddle as work-in-progress and 0BSD licensed. The download URL
was found on the official page, but the ZIP has **not** been retrieved, unpacked,
built or validated by this project. Do not report an executable emulator.

## Next reproducible steps

1. Download the ZIP through a browser, and check that it is a valid archive.
2. Inspect Cargo.toml, workspace crates, and LICENSE; record source hash/version.
3. Locate the emulation API (AudioEngine, process_zoom_block, host callbacks)
   and reconcile it with the upstream test rig:
   https://github.com/themanro/ZoomMultistompZDL/blob/main/docs/EMULATOR-TESTING.md
4. Run a single open-source ZDL through the emulator, first initialization and
   then deterministic audio blocks; retain input/output WAV and test logs.
5. Only after verified offline processing, assess latency, Windows ASIO and
   six-effect chaining. The existing six-slot desktop app is inspection-only.

Warning: the emulator may model C674x instructions but not every Zoom firmware
service. Emulator success is not proof of pedal hardware compatibility.
