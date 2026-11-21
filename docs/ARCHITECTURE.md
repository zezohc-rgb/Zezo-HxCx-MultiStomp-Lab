# Zezo HxCx MultiStomp Lab — Architecture

Target: Zoom MS-70CDR original (blue), firmware 2.10 reference, Windows 10 x64.

## Goals
- Load and inspect original and modified .zdl files.
- Execute actual C674x DSP code with emulated Zoom host services; report unsupported calls.
- Chain six stereo slots with bypass, parameters, preset save/load.
- Real-time audio through ASIO, including Fast Track MKII.
- Show measured or explicitly estimated DSP consumption and hardware-calibrated limits.
- Operate without a connected pedal or proprietary firmware at runtime, if technically validated.

## Modules
1. ZDL loader and dependency analyzer.
2. C674x CPU and memory emulator.
3. Zoom host compatibility services.
4. Six-slot stereo audio processing graph.
5. DSP budget and diagnostics.
6. Windows ASIO audio backend.
7. Desktop interface and packaging.

## Validation gates
- Parse a legally obtained test ZDL and identify dependencies.
- Execute its audio routine in deterministic offline tests.
- Verify six-slot chain, stereo routing, and real-time deadlines.
- Compare against physical MS-70CDR recordings and DSP limits.
- Package and test installer on Windows 10.

This is a specification, not proof that universal ZDL emulation already works. Do not bundle proprietary firmware or effects.
