param([Parameter(Mandatory=$true)][string]$Installer)
$ErrorActionPreference = 'Stop'
$setup = (Resolve-Path -LiteralPath $Installer).Path
$target = Join-Path $env:RUNNER_TEMP ('OpenVisioInstallerSmoke-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $target | Out-Null
try {
  $proc = Start-Process -FilePath $setup -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/DIR="' + $target + '"')) -Wait -PassThru
  if ($proc.ExitCode -ne 0) { throw "Installer failed: exit code $($proc.ExitCode)" }
  $exe = Join-Path $target 'OpenVisio.exe'
  if (!(Test-Path -LiteralPath $exe)) { throw "Installed OpenVisio.exe missing" }
  & (Join-Path $PSScriptRoot 'Smoke-Portable-Windows.ps1') -Executable $exe
  Write-Host 'PASS: silent installer creates an independently runnable OpenVisio.exe'
} finally {
  $uninstaller = Join-Path $target 'unins000.exe'
  if (Test-Path -LiteralPath $uninstaller) {
    $proc = Start-Process -FilePath $uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -Wait -PassThru
    if ($proc.ExitCode -ne 0) { Write-Warning "Uninstaller returned $($proc.ExitCode)" }
  }
  Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction SilentlyContinue
}
