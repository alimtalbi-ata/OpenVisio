param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path)
$ErrorActionPreference = 'Stop'
$package = Get-Content -Raw (Join-Path $Root 'package.json') | ConvertFrom-Json
$version = $package.version -replace '\.0$', ''
$exe = Join-Path $Root "dist/installer/OpenVisio-Setup-v$version-x64.exe"
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Missing installer: $exe" }
$file = Get-Item -LiteralPath $exe
if ($file.Length -lt 1000000) { throw 'Installer suspiciously small' }
$hash = Get-FileHash -LiteralPath $exe -Algorithm SHA256
$portablePath = Join-Path $Root "dist/portable/OpenVisio-v$version-Windows-x64-Portable.exe"
if (-not (Test-Path -LiteralPath $portablePath -PathType Leaf)) { throw "Missing portable: $portablePath" }
$portableFile = Get-Item -LiteralPath $portablePath
if ($portableFile.Length -lt 1000000) { throw 'Portable suspiciously small' }
$portableHash = Get-FileHash -LiteralPath $portablePath -Algorithm SHA256
# Validate Windows PE header, not just a filename or a size threshold.
foreach ($binary in @($exe, $portablePath)) {
 $stream = [System.IO.File]::OpenRead($binary)
 try {
  $header = New-Object byte[] 2
  if ($stream.Read($header,0,2) -ne 2 -or $header[0] -ne 0x4d -or $header[1] -ne 0x5a) { throw "Invalid PE/DOS header: $binary" }
 } finally { $stream.Dispose() }
}
$manifest = [ordered]@{
 product='OpenVisio'; version=$package.version; platform='win-x64'; author='Abdelhalim Talbi'; generatedUtc=(Get-Date).ToUniversalTime().ToString('o');
 artifacts=@(
  [ordered]@{kind='installer'; filename=$file.Name; bytes=$file.Length; sha256=$hash.Hash},
  [ordered]@{kind='portable'; filename=$portableFile.Name; bytes=$portableFile.Length; sha256=$portableHash.Hash}
 )
}
$target = Join-Path $Root 'dist/installer/release-manifest.json'
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $target -Encoding UTF8
Write-Host "PASS: $target (installer + portable)"
