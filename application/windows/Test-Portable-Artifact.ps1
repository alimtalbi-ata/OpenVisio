# Portable artifact verification, independent of installer. Author: Abdelhalim Talbi.
param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path)
$ErrorActionPreference = 'Stop'
$version = (Get-Content -Raw (Join-Path $Root 'package.json') | ConvertFrom-Json).version -replace '\.0$', ''
$portable = Join-Path $Root "dist/portable/OpenVisio-v$version-Windows-x64-Portable.exe"
if (-not (Test-Path -LiteralPath $portable -PathType Leaf)) { throw "Portable missing: $portable" }
$file = Get-Item -LiteralPath $portable
if ($file.Length -lt 1000000) { throw 'Portable suspiciously small' }
$stream = [IO.File]::OpenRead($portable)
try {
 $magic = New-Object byte[] 2
 if ($stream.Read($magic,0,2) -ne 2 -or $magic[0] -ne 77 -or $magic[1] -ne 90) { throw 'Portable missing MZ header' }
} finally { $stream.Dispose() }
$hash = (Get-FileHash -LiteralPath $portable -Algorithm SHA256).Hash
$manifestPath = Join-Path $Root 'dist/installer/release-manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) { throw 'Release manifest missing' }
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
$entry = @($manifest.artifacts | Where-Object { $_.kind -eq 'portable' })
if ($entry.Count -ne 1) { throw 'Manifest must have exactly one portable entry' }
if ($entry[0].filename -ne $file.Name -or $entry[0].bytes -ne $file.Length -or $entry[0].sha256 -ne $hash) { throw 'Portable manifest mismatch' }
Write-Host "PASS: portable artifact and SHA256 $hash"
