# Native executable smoke test. Author: Abdelhalim Talbi.
param([string]$Exe = 'dist/windows-x64/OpenVisio.exe', [int]$WaitSeconds = 12)
$ErrorActionPreference = 'Stop'
$resolved = (Resolve-Path $Exe).Path
$p = Start-Process -FilePath $resolved -PassThru
try {
 Start-Sleep -Seconds $WaitSeconds
 $p.Refresh()
 if ($p.HasExited) { throw "OpenVisio exited during smoke test (exit code $($p.ExitCode))" }
 Write-Host "PASS: OpenVisio process running after $WaitSeconds seconds (PID $($p.Id))"
} finally {
 if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
