# V43.21 independent GitHub checkout, engine SHA, mirror parity, and test gate.
# Author: Abdelhalim Talbi. Candidate only; never modifies main.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4321-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.21-canonical-archive-paths-20261025'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) { throw "Destination must not exist: $Destination" }
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'Independent checkout failed' }
Push-Location $Destination
try {
    $head = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve checkout HEAD' }
    if ($env:OPENVISIO_EXPECTED_SOURCE_SHA -and $head -ne $env:OPENVISIO_EXPECTED_SOURCE_SHA) { throw "Independent branch checkout $head differs from expected source SHA $env:OPENVISIO_EXPECTED_SOURCE_SHA" }
    $expected = @{
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/vsdx.py' = '7d9c561a9c70e8d9dec03ed25982ea65b8a04ce6'
        'python/openvisio/vsdx.py' = '7d9c561a9c70e8d9dec03ed25982ea65b8a04ce6'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/routing.py' = '15de75b0b4db520e92ca6d1df0e273ed022b607a'
        'python/openvisio/routing.py' = '15de75b0b4db520e92ca6d1df0e273ed022b607a'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/tests/test_low_zoom_label_lod_v4320.py' = 'f27363d69717142015065ea5613a34d769704d05'
        '04-Tests/tests/test_low_zoom_label_lod_v4320.py' = 'f27363d69717142015065ea5613a34d769704d05'
        'python/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '04-Tests/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '02-Compilation/verify_release_archive.py' = '925433adfefff0508ce776650a6a2f69ee5e4c39'
        'python/tests/test_release_archive_guard_v4320.py' = '9bac93b0b9f6c7d24056b6ce526731fcc9e0f523'
        '04-Tests/tests/test_release_archive_guard_v4320.py' = '9bac93b0b9f6c7d24056b6ce526731fcc9e0f523'
        'python/tests/test_vsdx_zip_path_canonical_v4321.py' = '7c301aba81831db84e6964a6e94cf91d96f17bc0'
        '04-Tests/tests/test_vsdx_zip_path_canonical_v4321.py' = '7c301aba81831db84e6964a6e94cf91d96f17bc0'
        '02-Compilation/Build-Windows-V43.21-Candidate.ps1' = '042efd09096cfdfdee7c97a0390ac207d0905937'
        '02-Compilation/generate_release_docs_v4321.py' = '7e9ff7245477ba6ef8daba131d8314724610014b'
        '02-Compilation/package_cumulative_release_v4321.py' = '50061b1c9a0100e6665bb78a519196f17af0f47d'
        '02-Compilation/requirements-build.txt' = '23feee4dfbc0ba8ee8e1c2062ea083ed5bf9d6c7'
        '02-Compilation/installer/OpenVisio-V43.21-Candidate.iss' = '463597406eded285759c11f8b2ffbdbe4b12402e'
        'README.md' = '6a492a7489236d4990d7e00e378dc7f3bccddd13'
        '05-Documentation/V43.21-CANONICAL-PATHS.md' = '7e7f3e73f8054754b92302dc2d199497361d034f'
        '05-Documentation/V43.21-CANONICAL-PATHS.svg' = 'ced9ec833ba56b19ac45751a070972d6ef2972c9'
        '05-Documentation/V43.21-WINDOWS-SCREENSHOTS-STATUS.md' = '66f504a440fb108d6310ae0fd9eb6f6249de2107'
        '.github/workflows/openvisio-v43.21-windows-candidate.yml' = 'e7236f816f0922a26fc40d4c58963c522b1e7b85'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing critical source: $path" }
        $actual = (git rev-parse "HEAD:$path").Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) { throw "Git blob mismatch: $path expected $($expected[$path]) got $actual" }
    }
    $status = (git status --porcelain).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect checkout status' }
    if ($status) { throw "Checkout is not clean: $status" }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source/test mirror parity failed' }
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.21
    if ($LASTEXITCODE -ne 0) { throw 'Cumulative release source guard failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent checkout $head, critical engine blob identities, mirror parity, and complete Python suite"
} finally { Pop-Location }
