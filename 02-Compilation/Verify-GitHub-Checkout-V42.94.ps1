# Reproducible independent checkout of the OpenVisio V42.94 candidate.
# Author: Abdelhalim Talbi. Does not modify main or production.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4294-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v42.94-san-null-metadata-ci-recovery-20261024'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) {
    throw "Destination must not exist; choose an empty path: $Destination"
}
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'GitHub checkout failed' }
Push-Location $Destination
try {
    $head = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve checkout HEAD' }
    $expected = @{
        'python/openvisio/model.py' = '747522deae7dbd5eee321726cc2df2095f9f7601'
        'python/openvisio/vsdx.py' = '0f5d8f4d2b0f23bef065d4700e0487a6b45a9af6'
        'python/openvisio/render.py' = 'f27dec0e2a96de9a86d34c4b669faaef45e88f9f'
        'python/openvisio/export.py' = '54f799d95d3e8b8050b34c848cab22601a8fcd64'
        'python/openvisio/retained_canvas.py' = '5c2d81ba7def18a00f6bf2a7f0b3d6dd047c04bf'
        'python/openvisio/shape_icons.py' = '4dc8bb45938f6908af09fa4c0045e89e244205f4'
        'python/openvisio/connector_labels.py' = '3740ae616d608ad15b9d851ebc067ba8656a376d'
        'python/tests/test_connector_blank_label_v4294.py' = '731ef7de52a9fcc12b9c78b167506adc1442df0d'
    }
    foreach ($path in $expected.Keys) {
        $actual = (git hash-object -- $path).Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) {
            throw "Git blob mismatch: $path expected $($expected[$path]) got $actual"
        }
    }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Mirror parity failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent GitHub checkout $head, critical engine SHA, mirrors and tests"
} finally {
    Pop-Location
}
