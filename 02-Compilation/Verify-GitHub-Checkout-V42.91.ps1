# Reproducible independent checkout of the OpenVisio V42.91 candidate.
# Author: Abdelhalim Talbi. Does not modify main or production.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4291-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v42.91-san-multipath-template-20261024'
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
        'python/openvisio/render.py' = '575b98d7a390c8acd0c2d2e5c45aef49aac8a220'
        'python/openvisio/templates.py' = '39f56c63ead1203d7f84aadb7f79dd93dd038d33'
        'python/tests/test_san_multipath_template_v4291.py' = 'e480297a94124fbe6dcf0b4c0881e2168f4a749f'
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
