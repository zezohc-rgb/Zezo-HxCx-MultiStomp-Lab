# Zezo MultiStomp VST3 — plano de integração verificado no código-fonte

Fonte inspecionada: arquivo enviado `ziddle-1794645921.zip`, caminhos `ziddle/shells/cli/src/plugin_cli.rs`, `ziddle/shells/vst3-headless/Cargo.toml`, `ziddle/shells/vst3-adapter/Cargo.toml`.

## Resultado da inspeção

- O pacote **já implementa** adaptador VST3 (`ziddle-vst3-adapter`) e biblioteca exportável (`ziddle-vst3-headless`).
- O comando `ziddle plugin build PATCH OUT_DIR --format vst3` gera um plugin **a partir de um patch**, não de um arquivo ZDL isolado.
- A criação do plugin resolve os efeitos e usa `native_prepare::compiler` e `native_prepare::prepare`; requer compilador Zig e a qualificação do efeito antes de empacotar.
- `plugin_cli.rs` exige que `ziddle_vst3_headless.dll` esteja ao lado de `ziddle.exe` no Windows.
- Um arquivo `.ZDL` por si só não satisfaz o argumento PATCH. Será necessário construir um patch válido que referencie o CE-2 Soul e fornecer as dependências do firmware.
- O firmware Zoom é de terceiros: não publicar no repositório público sem permissão. Evitar distribuir plugin contendo tradução de código Zoom.

## Critérios objetivos de conclusão

1. Compilar `ziddle.exe` e `ziddle_vst3_headless.dll` no Windows (workflow separado).
2. Construir patch de um slot com CE-2 Soul e resolver firmware, sem colocar arquivos proprietários em commits públicos.
3. Executar `ziddle plugin build` e confirmar a criação de um bundle `.vst3`.
4. Testar carregamento no Reaper e áudio real via Fast Track MKII; medir latência, bypass, parâmetros Rate/Depth.
5. Somente depois expandir para seis slots.

## Estado

A compilação do CLI foi confirmada anteriormente; a compilação do adaptador VST3, a preparação nativa, a criação de bundle e o áudio real ainda **não foram confirmados**. Não confundir biblioteca DLL com plugin final pronto para o Reaper.
