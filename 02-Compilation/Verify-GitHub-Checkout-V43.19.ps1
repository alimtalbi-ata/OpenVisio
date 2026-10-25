# V43.19 independent GitHub checkout, engine SHA, mirror parity, and test gate.
# Author: Abdelhalim Talbi. Candidate only; never modifies main.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4319-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.19-no-label-truncation-20261025'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) { throw "Destination must not exist: $Destination" }
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'Independent checkout failed' }
Push-Location $Destination
try {
    $head = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve checkout HEAD' }
    if ($env:GITHUB_SHA -and $head -ne $env:GITHUB_SHA) { throw "Checkout $head differs from CI commit $env:GITHUB_SHA" }
    $expected = @{
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/vsdx.py' = '003a192c8a607e8e8f4e3313ef07b03b785a0314'
        '03-Sources/openvisio/vsdx.py' = '003a192c8a607e8e8f4e3313ef07b03b785a0314'
        'python/openvisio/render.py' = '92f1f9eedf22c6f75558710737de85631a710553'
        '03-Sources/openvisio/render.py' = '92f1f9eedf22c6f75558710737de85631a710553'
        'python/openvisio/export.py' = 'dc2078b3212930163342d330b43483185a34de0c'
        '03-Sources/openvisio/export.py' = 'dc2078b3212930163342d330b43483185a34de0c'
        'python/openvisio/node_labels.py' = '28d4d2ecc13babb8b337e3ef846b05d37f5b29b3'
        '03-Sources/openvisio/node_labels.py' = '28d4d2ecc13babb8b337e3ef846b05d37f5b29b3'
        'python/openvisio/connector_labels.py' = '2d324a8e0eaffcc5a6096dfdcbf425415d63e9e3'
        '03-Sources/openvisio/connector_labels.py' = '2d324a8e0eaffcc5a6096dfdcbf425415d63e9e3'
        'python/tests/test_svg_multiline_labels_v4318.py' = '15e284345ba50797c7927208cd07d90cfe8d7668'
        '04-Tests/tests/test_svg_multiline_labels_v4318.py' = '15e284345ba50797c7927208cd07d90cfe8d7668'
        'python/tests/test_node_label_fidelity_v4319.py' = '181f37237f99920020a3fea6e715b3e906fe3d70'
        '04-Tests/tests/test_node_label_fidelity_v4319.py' = '181f37237f99920020a3fea6e715b3e906fe3d70'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing critical source: $path" }
        $actual = (git rev-parse "HEAD:$path").Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) { throw "Git blob mismatch: $path expected $($expected[$path]) got $actual" }
    }
    git diff --exit-code -- .
    if ($LASTEXITCODE -ne 0) { throw 'Checkout differs from committed tree' }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source/test mirror parity failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent checkout $head, critical engine blob identities, mirror parity, and complete Python suite"
} finally { Pop-Location }
