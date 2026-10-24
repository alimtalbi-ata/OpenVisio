# OpenVisio V42.98 source candidate — native Windows x64 build and smoke.
# Internal application version remains 42.50.0 due to legacy build contracts.
# Candidate only: NOT a production release or Microsoft Visio certification.
# Author: Abdelhalim Talbi.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $root
try {
    $env:PYTHONPATH = Join-Path $root 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source mirrors differ' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python suite failed' }
    python -m pip install --disable-pip-version-check -r '02-Compilation/requirements-build.txt'
    if ($LASTEXITCODE -ne 0) { throw 'Pinned PyInstaller installation failed' }
    $portable = Join-Path $root 'dist/OpenVisio-V42.98-Source-Candidate-Windows-x64-Portable.exe'
    $installer = Join-Path $root 'dist/installer/OpenVisio-V42.98-Source-Candidate-Setup-x64.exe'
    foreach ($file in @($portable, $installer)) {
        if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file -Force }
    }
    python -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name OpenVisio-V42.98-Source-Candidate-Windows-x64-Portable `
        --paths python python/run_openvisio.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
    if (!(Test-Path -LiteralPath $portable)) { throw 'Portable EXE absent' }
    & (Join-Path $root '04-Tests/Smoke-Portable-V42.71.ps1') -Executable $portable
    if ($LASTEXITCODE -ne 0) { throw 'Frozen functional smoke failed' }
    $iscc = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6/ISCC.exe'
    if (!(Test-Path -LiteralPath $iscc)) { throw 'Inno Setup 6 absent' }
    & $iscc '02-Compilation/installer/OpenVisio-V42.98-Candidate.iss'
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed' }
    if (!(Test-Path -LiteralPath $installer)) { throw 'Installer EXE absent' }
    & (Join-Path $root '04-Tests/Smoke-Installer-V42.71.ps1') -Installer $installer
    if ($LASTEXITCODE -ne 0) { throw 'Installer functional smoke failed' }
    $manifest = Join-Path $root 'dist/OpenVisio-V42.98-Source-Candidate-Windows-SHA256.txt'
    @($portable, $installer) | ForEach-Object {
        $hash = Get-FileHash -LiteralPath $_ -Algorithm SHA256
        "$($hash.Hash.ToLowerInvariant())  $([IO.Path]::GetFileName($_))"
    } | Set-Content -LiteralPath $manifest -Encoding ascii
    Write-Host 'PASS: Windows source candidate compiled and functional smoke completed'
} finally {
    Pop-Location
}
