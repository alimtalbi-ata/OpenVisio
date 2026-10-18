# Windows-only startup smoke tests. Author: Abdelhalim Talbi.
param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
      [ValidateSet('Portable','Native')][string]$Mode = 'Portable',
      [int]$WaitSeconds = 8,
      [string]$ReportDir = '')
$ErrorActionPreference = 'Stop'
if ($WaitSeconds -lt 1 -or $WaitSeconds -gt 120) { throw 'WaitSeconds must be 1..120' }
$version = (Get-Content -Raw (Join-Path $Root 'package.json') | ConvertFrom-Json).version -replace '\.0$', ''
if (!$ReportDir) { $ReportDir = Join-Path $Root 'dist/qualification' }
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$exe = if ($Mode -eq 'Portable') { Join-Path $Root "dist/portable/OpenVisio-v$version-Windows-x64-Portable.exe" } else { Join-Path $Root 'dist/windows-x64/OpenVisio.exe' }
$report = [ordered]@{ mode=$Mode; version=$version; executable=$exe; startup='NOT_RUN'; wait_seconds=$WaitSeconds; error=$null }
$process = $null
try {
 if (!(Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Missing executable: $exe" }
 if ((Get-Item -LiteralPath $exe).Length -lt 1000000) { throw 'Executable suspiciously small' }
 $stream = [IO.File]::OpenRead($exe)
 try { $bytes = New-Object byte[] 2; if ($stream.Read($bytes,0,2) -ne 2 -or $bytes[0] -ne 77 -or $bytes[1] -ne 90) { throw 'Invalid PE/MZ header' } } finally { $stream.Dispose() }
 $process = Start-Process -FilePath $exe -PassThru
 Start-Sleep -Seconds $WaitSeconds
 $process.Refresh()
 if ($process.HasExited) { throw "Application exited unexpectedly with code $($process.ExitCode)" }
 $report.startup = 'PASS'
 Write-Host "PASS: $Mode startup, PID $($process.Id)"
} catch {
 $report.startup = 'FAIL'; $report.error = $_.Exception.Message
 throw
} finally {
 if ($null -ne $process) {
  try { $process.Refresh(); if (!$process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue } } finally { $process.Dispose() }
 }
 $report | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 (Join-Path $ReportDir "startup-$($Mode.ToLowerInvariant()).json")
}
