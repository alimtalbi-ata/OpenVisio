param([Parameter(Mandatory=$true)][string]$Executable)
$ErrorActionPreference = 'Stop'
$path = (Resolve-Path -LiteralPath $Executable).Path
$isolated = Join-Path $env:TEMP ('openvisio-smoke-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $isolated | Out-Null
$copy = Join-Path $isolated 'OpenVisio.exe'
Copy-Item -LiteralPath $path -Destination $copy
$process = $null
try {
  $process = Start-Process -FilePath $copy -WorkingDirectory $isolated -PassThru
  Start-Sleep -Seconds 12
  $process.Refresh()
  if ($process.HasExited) { throw "Portable EXE exited during startup with code $($process.ExitCode)" }
  Write-Host 'PASS: portable launches outside source tree and stays running'
} finally {
  if ($process -and -not $process.HasExited) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    $process.WaitForExit(10000) | Out-Null
  }
  Remove-Item -LiteralPath $isolated -Recurse -Force -ErrorAction SilentlyContinue
}
