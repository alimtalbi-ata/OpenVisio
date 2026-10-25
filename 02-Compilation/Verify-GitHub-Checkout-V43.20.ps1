# V43.20 independent GitHub checkout, engine SHA, mirror parity, and test gate.
# Author: Abdelhalim Talbi. Candidate only; never modifies main.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4320-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.20-source-reconciliation-20261025'
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
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/export.py' = 'b376736830a1ee6b9cd8720d6f349528600a8d7a'
        '03-Sources/openvisio/export.py' = 'b376736830a1ee6b9cd8720d6f349528600a8d7a'
        'python/openvisio/node_labels.py' = 'f780edc2653f30134ba333ae39bb8e219949097f'
        '03-Sources/openvisio/node_labels.py' = 'f780edc2653f30134ba333ae39bb8e219949097f'
        'python/openvisio/connector_labels.py' = '2d324a8e0eaffcc5a6096dfdcbf425415d63e9e3'
        '03-Sources/openvisio/connector_labels.py' = '2d324a8e0eaffcc5a6096dfdcbf425415d63e9e3'
        'python/tests/test_svg_multiline_labels_v4318.py' = '15e284345ba50797c7927208cd07d90cfe8d7668'
        '04-Tests/tests/test_svg_multiline_labels_v4318.py' = '15e284345ba50797c7927208cd07d90cfe8d7668'
        'python/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '04-Tests/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '02-Compilation/verify_release_archive.py' = '6299b9c2e84d7bca285d119dd9039b7b19a64c55'
        'python/tests/test_release_archive_guard_v4320.py' = 'f05a218af5fd10924adb779275c5d9b776f6f8f4'
        '04-Tests/tests/test_release_archive_guard_v4320.py' = 'f05a218af5fd10924adb779275c5d9b776f6f8f4'
        'python/tests/test_low_zoom_label_lod_v4320.py' = '292d89c3763f32ecad39908067a36fcf1b42c80d'
        '04-Tests/tests/test_low_zoom_label_lod_v4320.py' = '292d89c3763f32ecad39908067a36fcf1b42c80d'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing critical source: $path" }
        $actual = (git rev-parse "HEAD:$path").Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) { throw "Git blob mismatch: $path expected $($expected[$path]) got $actual" }
        '02-Compilation/verify_release_archive.py' = '6299b9c2e84d7bca285d119dd9039b7b19a64c55'
        'python/tests/test_release_archive_guard_v4320.py' = 'f05a218af5fd10924adb779275c5d9b776f6f8f4'
        '04-Tests/tests/test_release_archive_guard_v4320.py' = 'f05a218af5fd10924adb779275c5d9b776f6f8f4'
        'python/tests/test_low_zoom_label_lod_v4320.py' = '292d89c3763f32ecad39908067a36fcf1b42c80d'
        '04-Tests/tests/test_low_zoom_label_lod_v4320.py' = '292d89c3763f32ecad39908067a36fcf1b42c80d'
    }
    git diff --exit-code -- .
    if ($LASTEXITCODE -ne 0) { throw 'Checkout differs from committed tree' }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source/test mirror parity failed' }
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.20
    if ($LASTEXITCODE -ne 0) { throw 'Cumulative release source guard failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent checkout $head, critical engine blob identities, mirror parity, and complete Python suite"
} finally { Pop-Location }
