# Ziddle source ZIP inspected — 2026-11-21

The user supplied `ziddle-1794645921.zip`. The archive was inspected locally
without downloading or executing untrusted code.

- ZIP size: **1,802,092 bytes**
- SHA-256: `96d083ab78d6b8c6336a11adcc042044d6f255ba2e81dfa79210a6591e984502`
- 648 archive entries; ZIP CRC test passed.
- 52 `Cargo.toml` manifests, including the workspace root.
- Root Cargo workspace version `0.1.0`, edition `2021`, license `0BSD`.
- Relevant crates:
  - `ziddle/runtime/c674x-cpu`
  - `ziddle/runtime/effect-emulator`
  - `ziddle/audio/offline-renderer`
  - `ziddle/audio/effect-chain`
  - `ziddle/shells/cli`
  - `ziddle/shells/vst3-adapter`
  - `ziddle/shells/clap-adapter`
- `ziddle/shells/cli/Cargo.toml` declares a binary named `ziddle`,
  described as an offline effect runner.

## Corrected integration approach

The old external `matcheck` harness was documented against a different
Ziddle workspace layout. **Do not assume it is compatible with this archive.**
Prefer the included `ziddle` CLI and offline-renderer implementation, and
inspect its current command syntax with `ziddle --help` after compilation.

The present execution environment has **no `cargo` or `rustc` executable**,
so no Rust build, ZDL execution, Windows ASIO validation, or audio rendering
was performed. The source archive itself was verified, not its behavior.

### Next experiment

On Windows with Rust installed, unpack the archive and run from its root:

```powershell
cargo build --release -p ziddle-cli --bin ziddle
.\target\release\ziddle.exe --help
```

Capture compiler output and the available offline-render subcommands. Then
run an openly distributable ZDL on a known WAV and compare output to input.
Do not claim success until actual audio samples are produced.
