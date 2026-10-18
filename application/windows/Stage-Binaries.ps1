# Author: Abdelhalim Talbi. Only genuine built artifacts are staged.
param(
 [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
 [ValidateSet('Report','RequireValid')][string]$SignaturePolicy = 'Report'
)
$ErrorActionPreference = 'Stop'
[xml]$project = Get-Content (Join-Path $Root 'windows/native/OpenVisio.csproj') -Raw
$version = [string]$project.Project.PropertyGroup.Version
if ($version -notmatch '^(\d+)\.(\d+)\.\d+$') { throw 'Version invalide' }
$v = "$($Matches[1]).$($Matches[2])"
$items = @(
 @{ Kind='installer'; Source="dist/installer/OpenVisio-Setup-v$v-x64.exe"; Dest="OpenVisio-Setup-v$v-x64.exe" },
 @{ Kind='portable'; Source="dist/portable/OpenVisio-v$v-Windows-x64-Portable.exe"; Dest="OpenVisio-v$v-Windows-x64-Portable.exe" }
)
$out = Join-Path $Root 'binary'
# Never expose a mixed release: prepare both files in a private staging directory.
$pending = Join-Path $Root 'binary.pending'
$previous = Join-Path $Root 'binary.previous'
if (Test-Path -LiteralPath $pending) { throw 'Publication interrompue precedente: binary.pending existe. Inspection manuelle requise.' }
if (Test-Path -LiteralPath $previous) { throw 'Sauvegarde binary.previous existante: inspection manuelle requise avant publication.' }
New-Item -ItemType Directory -Force -Path $pending | Out-Null
$report = @{ version=$v; status='FAIL'; signaturePolicy=$SignaturePolicy; artifacts=@() }
try {
 foreach ($item in $items) {
  $src = Join-Path $Root $item.Source
  if (!(Test-Path -LiteralPath $src)) { throw "Binaire absent: $src" }
  $f = Get-Item -LiteralPath $src
  if ($f.Length -lt 1000000) { throw "Binaire trop petit: $src" }
  $stream=[System.IO.File]::OpenRead($src)
  try { if ($stream.ReadByte() -ne 77 -or $stream.ReadByte() -ne 90) { throw "En-tete MZ invalide: $src" } } finally { $stream.Dispose() }
  $dst=Join-Path $pending $item.Dest
  Copy-Item -LiteralPath $src -Destination $dst -Force
  $hash=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash
  $sig=Get-AuthenticodeSignature -LiteralPath $dst
  $sigStatus=[string]$sig.Status
  if ($SignaturePolicy -eq 'RequireValid' -and $sigStatus -ne 'Valid') { throw "Signature Authenticode invalide: $dst ($sigStatus)" }
  $signer=$null
  if ($sig.SignerCertificate) { $signer=$sig.SignerCertificate.Subject }
  $report.artifacts += @{kind=$item.Kind; file=$item.Dest; bytes=$f.Length; sha256=$hash; signatureStatus=$sigStatus; signer=$signer }

 }
 $report.status='PASS'
 $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $pending 'manifest.json') -Encoding UTF8
 # Swap only after BOTH artifacts and the manifest are verified.
 if (Test-Path -LiteralPath $out) { Move-Item -LiteralPath $out -Destination $previous }
 try { Move-Item -LiteralPath $pending -Destination $out }
 catch {
  if (!(Test-Path -LiteralPath $out) -and (Test-Path -LiteralPath $previous)) { Move-Item -LiteralPath $previous -Destination $out }
  throw
 }
 # Preserve binary.previous as a recovery checkpoint; do not delete it automatically.
} catch {
 $report.error = $_.Exception.Message
 $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $Root 'binary-publication-failure.json') -Encoding UTF8
 throw
}
if ($report.status -ne 'PASS') { exit 1 }
Write-Host "Livrables Windows copies dans $out"
