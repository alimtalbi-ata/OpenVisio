# Author: Abdelhalim Talbi. Read-only recovery assessment by default.
param(
 [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
 [switch]$RestorePrevious,
 [switch]$ConfirmRecovery
)
$ErrorActionPreference = 'Stop'
$binary = Join-Path $Root 'binary'
$previous = Join-Path $Root 'binary.previous'
$pending = Join-Path $Root 'binary.pending'
$reportPath = Join-Path $Root 'binary-recovery-assessment.json'
function Test-Release($directory) {
 if (!(Test-Path -LiteralPath $directory -PathType Container)) { return $false }
 $manifestPath = Join-Path $directory 'manifest.json'
 if (!(Test-Path -LiteralPath $manifestPath -PathType Leaf)) { return $false }
 try {
  $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
  if ($manifest.status -ne 'PASS' -or @($manifest.artifacts).Count -ne 2) { return $false }
  $kinds = @($manifest.artifacts | ForEach-Object { $_.kind })
  if (!($kinds -contains 'installer') -or !($kinds -contains 'portable')) { return $false }
  $names = @($manifest.artifacts | ForEach-Object { $_.file })
  if (@($names | Sort-Object -Unique).Count -ne 2) { return $false }
  if (@($names | Where-Object { $_ -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*\.exe$' }).Count -gt 0) { return $false }
  foreach ($artifact in $manifest.artifacts) {
   if ([string]::IsNullOrWhiteSpace($artifact.file) -or $artifact.file -ne [System.IO.Path]::GetFileName($artifact.file)) { return $false }
   $path = Join-Path $directory $artifact.file
   if (!(Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
   if ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { return $false }
   $item = Get-Item -LiteralPath $path
   if ($item.Length -lt 1000000 -or $item.Length -ne [long]$artifact.bytes) { return $false }
   $stream = [System.IO.File]::OpenRead($path)
   try { if ($stream.ReadByte() -ne 77 -or $stream.ReadByte() -ne 90) { return $false } } finally { $stream.Dispose() }
   if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $artifact.sha256) { return $false }
  }
  return $true
 } catch { return $false }
}
$assessment = [ordered]@{
 timestamp = (Get-Date).ToUniversalTime().ToString('o')
 binaryValid = (Test-Release $binary)
 previousValid = (Test-Release $previous)
 pendingPresent = (Test-Path -LiteralPath $pending)
 action = 'INSPECT_ONLY'
 status = 'PASS'
}
try {
 if ($RestorePrevious) {
  if (!$ConfirmRecovery) { throw 'Restauration refusee: -ConfirmRecovery obligatoire.' }
  if ($assessment.pendingPresent) { throw 'Restauration refusee: binary.pending existe.' }
  if (!$assessment.previousValid) { throw 'Restauration refusee: binary.previous invalide.' }
  if ($assessment.binaryValid) { throw 'Restauration refusee: binary actuel valide.' }
  if (Test-Path -LiteralPath $binary) { throw 'Restauration refusee: binary actuel existe; sauvegarde manuelle requise.' }
  Move-Item -LiteralPath $previous -Destination $binary
  if (!(Test-Release $binary)) {
   # Restore the checkpoint if the final validation fails. Never report success.
   if (!(Test-Path -LiteralPath $previous) -and (Test-Path -LiteralPath $binary)) { Move-Item -LiteralPath $binary -Destination $previous }
   throw 'Restauration refusee: verification apres deplacement echouee.'
  }
  $assessment.binaryValid = $true
  $assessment.previousValid = $false
  $assessment.action = 'RESTORED_PREVIOUS'
 }
} catch {
 $assessment.status = 'FAIL'
 $assessment.error = $_.Exception.Message
 throw
} finally {
 $assessment | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $reportPath -Encoding UTF8
}
Write-Host "Assessment: $reportPath"
