# V43.08 independent Windows checkout and SAN layer-lock regression gate.
# Author: Abdelhalim Talbi. No main or production modification.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4308-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.08-locked-san-geometry-20261024'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) {
    throw "Destination must not exist: $Destination"
}
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'Independent checkout failed' }
Push-Location $Destination
try {
    $head = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve checkout HEAD' }
    if ($env:GITHUB_SHA -and $head -ne $env:GITHUB_SHA) {
        throw "Checkout $head differs from CI commit $env:GITHUB_SHA"
    }
    $expected = @{
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/vsdx.py' = '0f5d8f4d2b0f23bef065d4700e0487a6b45a9af6'
        '03-Sources/openvisio/vsdx.py' = '0f5d8f4d2b0f23bef065d4700e0487a6b45a9af6'
        'python/openvisio/render.py' = '1709c39e1fbdda0b7dc1031ad06e915bf7f39467'
        '03-Sources/openvisio/render.py' = '1709c39e1fbdda0b7dc1031ad06e915bf7f39467'
        'python/openvisio/property_commands.py' = '9d44c08a5ddbbd574c71e35d2b9198447486c98a'
        '03-Sources/openvisio/property_commands.py' = '9d44c08a5ddbbd574c71e35d2b9198447486c98a'
        'python/tests/test_property_layer_lock_v4307.py' = '4fddda4cb29e27bd891d87f1022e6859e21f839b'
        '04-Tests/tests/test_property_layer_lock_v4307.py' = '4fddda4cb29e27bd891d87f1022e6859e21f839b'
        'python/openvisio/app.py' = 'f9dbf4b4bff13da3dfa60551be64b62f38bffabd'
        '03-Sources/openvisio/app.py' = 'f9dbf4b4bff13da3dfa60551be64b62f38bffabd'
        'python/openvisio/geometry_lock.py' = '0ed848d6d854f49247eacb53bb7fcaf4ce49e227'
        '03-Sources/openvisio/geometry_lock.py' = '0ed848d6d854f49247eacb53bb7fcaf4ce49e227'
        'python/tests/test_locked_san_geometry_v4308.py' = 'feeb497eb7da6a713cc4c8d1181368e0af797bb2'
        '04-Tests/tests/test_locked_san_geometry_v4308.py' = 'feeb497eb7da6a713cc4c8d1181368e0af797bb2'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing critical source: $path"
        }
        $actual = (git rev-parse "HEAD:$path").Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) {
            throw "Git blob mismatch: $path expected $($expected[$path]) got $actual"
        }
    }
    git diff --exit-code -- .
    if ($LASTEXITCODE -ne 0) { throw 'Checkout differs from committed tree' }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source/test mirror parity failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent checkout $head, engine/test SHA, mirror parity, Python suite"
} finally {
    Pop-Location
}
