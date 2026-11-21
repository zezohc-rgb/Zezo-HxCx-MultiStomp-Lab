# Build the supplied Ziddle source ZIP on Windows 10
# Usage: powershell -ExecutionPolicy Bypass -File .\build_ziddle_windows.ps1 -Archive C:\path\ziddle-1794645921.zip
param(
  [Parameter(Mandatory=$true)][string]$Archive,
  [string]$Destination = "$env:USERPROFILE\ZezoZiddle"
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) { throw 'Rust/Cargo ausente. Instale rustup em https://rustup.rs e abra novo PowerShell.' }
if (-not (Test-Path -LiteralPath $Archive -PathType Leaf)) { throw "ZIP não encontrado: $Archive" }
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Expand-Archive -LiteralPath $Archive -DestinationPath $Destination -Force
$manifest = Get-ChildItem -Path $Destination -Filter Cargo.toml -Recurse -File | Where-Object { (Get-Content -LiteralPath $_.FullName -Raw) -match '\[workspace\]' } | Select-Object -First 1
if (-not $manifest) { throw 'Cargo workspace raiz não encontrado.' }
Push-Location $manifest.DirectoryName
try {
  cargo build --release -p ziddle-cli --bin ziddle
  if ($LASTEXITCODE -ne 0) { throw "Compilação falhou: $LASTEXITCODE" }
  $exe = Join-Path (Get-Location) 'target\release\ziddle.exe'
  if (-not (Test-Path $exe)) { throw "Executável não encontrado: $exe" }
  & $exe effect render --help
  if ($LASTEXITCODE -ne 0) { throw 'Falha no help do renderizador.' }
  Write-Host "Ziddle compilado: $exe"
  Write-Host 'Uso: ziddle effect render EFFECT.ZDL entrada.wav saida.wav --firmware FIRMWARE'
  Write-Host 'Requer firmware compatível e WAV de 44,1 kHz. Nenhum áudio real foi testado.'
} finally { Pop-Location }
