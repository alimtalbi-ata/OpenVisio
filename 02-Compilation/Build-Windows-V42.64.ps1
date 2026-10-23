# OpenVisio V42.64 Windows release build (not yet qualified on Windows).
# Author: Abdelhalim Talbi. No force push, no production changes.
[CmdletBinding()]
param([switch]$SkipInstallSmoke)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $root
try {
    $env:PYTHONPATH = Join-Path $root 'python'
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python tests failed' }
    python -m pip install --disable-pip-version-check pyinstaller
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller installation failed' }
    $portable = Join-Path $root 'dist/OpenVisio-v42.64-Windows-x64-Portable.exe'
    $installer = Join-Path $root 'dist/installer/OpenVisio-Setup-v42.64-x64.exe'
    foreach ($file in @($portable, $installer)) {
        if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file -Force }
    }
    python -m PyInstaller --noconfirm --clean --onefile --windowed --name OpenVisio-v42.64-Windows-x64-Portable --paths python python/run_openvisio.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
    if (-not (Test-Path -LiteralPath $portable)) { throw 'Portable EXE absent' }
    if ((Get-Item $portable).Length -lt 1000000) { throw 'Portable EXE too small' }
    $iscc = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6/ISCC.exe'
    if (-not (Test-Path -LiteralPath $iscc)) {
        $command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
        if (-not $command) { throw 'Inno Setup 6 absent' }
        $iscc = $command.Source
    }
    & $iscc '02-Compilation/installer/OpenVisio-V42.64.iss'
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup build failed' }
    if (-not (Test-Path -LiteralPath $installer)) { throw 'Installer EXE absent' }
    if ((Get-Item $installer).Length -lt 1000000) { throw 'Installer EXE too small' }
    # Verify that the portable executable starts from a source-free directory.
    $isolated = Join-Path $env:TEMP 'OpenVisio-V42.64-Portable-Smoke'
    New-Item -ItemType Directory -Path $isolated -Force | Out-Null
    $isolatedExe = Join-Path $isolated 'OpenVisio.exe'
    Copy-Item -LiteralPath $portable -Destination $isolatedExe -Force
    $proc = Start-Process -FilePath $isolatedExe -PassThru
    try {
        Start-Sleep -Seconds 5
        if ($proc.HasExited) { throw "Portable EXE exited early ($($proc.ExitCode))" }
    } finally {
        if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
    }
    if (-not $SkipInstallSmoke) {
        $dest = Join-Path $env:TEMP 'OpenVisio-V42.64-Installer-Smoke'
        & $installer /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- "/DIR=$dest"
        if ($LASTEXITCODE -ne 0) { throw 'Silent installer failed' }
        if (-not (Test-Path -LiteralPath (Join-Path $dest 'OpenVisio.exe'))) { throw 'Installed EXE absent' }
        $uninstall = Join-Path $dest 'unins000.exe'
        if (-not (Test-Path -LiteralPath $uninstall)) { throw 'Uninstaller absent' }
        & $uninstall /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
        if ($LASTEXITCODE -ne 0) { throw 'Silent uninstall failed' }
    }
    $manifest = Join-Path $root 'dist/OpenVisio-V42.64-Windows-SHA256.txt'
    @($portable, $installer) | ForEach-Object {
        $h = Get-FileHash -LiteralPath $_ -Algorithm SHA256
        "$($h.Hash.ToLowerInvariant())  $([IO.Path]::GetFileName($_))"
    } | Set-Content -LiteralPath $manifest -Encoding ascii
    Write-Host 'PASS: Windows portable, installer and smoke tests'
} finally { Pop-Location }
