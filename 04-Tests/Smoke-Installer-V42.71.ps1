# Install, qualify frozen executable, uninstall. Actual Windows only.
# Author: Abdelhalim Talbi.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Installer)
$ErrorActionPreference = 'Stop'
$setup = (Resolve-Path -LiteralPath $Installer).Path
$target = Join-Path $env:TEMP ('OpenVisio-V4271-Installer-' + [guid]::NewGuid().ToString('N'))
try {
    $proc = Start-Process -FilePath $setup -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/DIR="' + $target + '"')) -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "Installer exit code $($proc.ExitCode)" }
    $exe = Join-Path $target 'OpenVisio.exe'
    if (!(Test-Path -LiteralPath $exe)) { throw 'Installed executable absent' }
    & (Join-Path $PSScriptRoot 'Smoke-Portable-V42.71.ps1') -Executable $exe
    if ($LASTEXITCODE -ne 0) { throw 'Installed executable functional smoke failed' }
    Write-Host 'PASS: installer and installed frozen executable'
} finally {
    $uninstaller = Join-Path $target 'unins000.exe'
    if (Test-Path -LiteralPath $uninstaller) {
        $proc = Start-Process -FilePath $uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -Wait -PassThru
        if ($proc.ExitCode -ne 0) { Write-Warning "Uninstaller exit code $($proc.ExitCode)" }
    }
    Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction SilentlyContinue
}
