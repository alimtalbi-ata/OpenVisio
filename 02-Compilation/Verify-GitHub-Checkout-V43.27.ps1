# OpenVisio V43.27 independent checkout and source-pinning gate.
# Fetches the exact commit selected by GitHub Actions; never writes to main.
# Author: Abdelhalim Talbi.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP ('openvisio-v4327-independent-' + [guid]::NewGuid().ToString('N'))))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
$expectedCommit = ([string]$env:OPENVISIO_EXPECTED_SOURCE_SHA).Trim()
if ($expectedCommit -notmatch '^[0-9a-f]{40}$') { throw 'OPENVISIO_EXPECTED_SOURCE_SHA must be a full commit SHA' }
if (Test-Path -LiteralPath $Destination) { throw "Destination must not exist: $Destination" }
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
git -C $Destination init
if ($LASTEXITCODE -ne 0) { throw 'Independent git init failed' }
git -C $Destination remote add origin $repo
if ($LASTEXITCODE -ne 0) { throw 'Independent origin setup failed' }
git -C $Destination fetch --depth 1 origin $expectedCommit
if ($LASTEXITCODE -ne 0) { throw 'Independent fetch of selected commit failed' }
git -C $Destination checkout --detach FETCH_HEAD
if ($LASTEXITCODE -ne 0) { throw 'Independent checkout of selected commit failed' }

Push-Location $Destination
try {
    $head = (@(git rev-parse HEAD) -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $head -ne $expectedCommit) { throw "Independent checkout commit mismatch: $head" }
    $expected = @{
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/vsdx.py' = '490e12f8d7a76e584ddc95830f23d68225a4f00e'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/routing.py' = 'b830d2e142c16b285e5057f9398fea31e99ea832'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        '03-Sources/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        '03-Sources/openvisio/vsdx_external.py' = '1efb836e63dc52b001ec4305b75dec4eaa093aa7'
        '03-Sources/openvisio/visio_formula.py' = 'ff3584c2cc9fc451aac99c5f2d8daf9721b51d78'
        '03-Sources/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        '03-Sources/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        '03-Sources/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        '03-Sources/openvisio/vsdx_geometry.py' = 'e89c85c50d05ffb66739aa2245ca8ae817dd25a4'
        '03-Sources/openvisio/app.py' = '145dadc50d1e03f856b63f5d0392fae5d4733016'
        '03-Sources/openvisio/export.py' = 'b376736830a1ee6b9cd8720d6f349528600a8d7a'
        '03-Sources/openvisio/shape_icons.py' = '798ae65b9f23c8b92632f59cf002f63ca95b44de'
        '03-Sources/openvisio/vsdx_audit.py' = '3ca0aa7b7545ebf4937d8ff7e26fa7a4bd55919a'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/vsdx.py' = '490e12f8d7a76e584ddc95830f23d68225a4f00e'
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/routing.py' = 'b830d2e142c16b285e5057f9398fea31e99ea832'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        'python/openvisio/vsdx_external.py' = '1efb836e63dc52b001ec4305b75dec4eaa093aa7'
        'python/openvisio/visio_formula.py' = 'ff3584c2cc9fc451aac99c5f2d8daf9721b51d78'
        'python/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        'python/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        'python/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        'python/openvisio/vsdx_geometry.py' = 'e89c85c50d05ffb66739aa2245ca8ae817dd25a4'
        'python/openvisio/app.py' = '145dadc50d1e03f856b63f5d0392fae5d4733016'
        'python/openvisio/export.py' = 'b376736830a1ee6b9cd8720d6f349528600a8d7a'
        'python/openvisio/shape_icons.py' = '798ae65b9f23c8b92632f59cf002f63ca95b44de'
        'python/openvisio/vsdx_audit.py' = '3ca0aa7b7545ebf4937d8ff7e26fa7a4bd55919a'
        'python/tests/test_vsdx_formula_geometry_fidelity_v4327.py' = '6dbe5c798f3bbf01e4a0da87e8a17f4c1cc161b0'
        'python/tests/test_vsdx_strict_fidelity_counters_v4327.py' = 'ace30638aba0478dabe9de88bc0b7005b553825d'
        'python/tests/test_vsdx_audit_v426.py' = 'ee8875d5ba80c407af39bf40ea58765a5ab3b0ec'
        'python/tests/test_visio_formula_v4327.py' = '6d426ab8278f124df55d1a27c31228c7382bfbce'
        '04-Tests/tests/test_vsdx_formula_geometry_fidelity_v4327.py' = '6dbe5c798f3bbf01e4a0da87e8a17f4c1cc161b0'
        '04-Tests/tests/test_vsdx_strict_fidelity_counters_v4327.py' = 'ace30638aba0478dabe9de88bc0b7005b553825d'
        '04-Tests/tests/test_vsdx_audit_v426.py' = 'ee8875d5ba80c407af39bf40ea58765a5ab3b0ec'
        '04-Tests/tests/test_visio_formula_v4327.py' = '6d426ab8278f124df55d1a27c31228c7382bfbce'
        'python/tests/test_vsdx_route_spatial_prefilter_v4325.py' = 'c413b3178c1a65dfa5dbd012bf017ff3a75b54d7'
        '04-Tests/tests/test_vsdx_route_spatial_prefilter_v4325.py' = 'c413b3178c1a65dfa5dbd012bf017ff3a75b54d7'
        'python/tests/test_vsdx_route_segment_prefilter_v4325.py' = '63a0cc6af4c56d2d0e721e5298acc7842e538d15'
        '04-Tests/tests/test_vsdx_route_segment_prefilter_v4325.py' = '63a0cc6af4c56d2d0e721e5298acc7842e538d15'
        '02-Compilation/Build-Windows-V43.27-Candidate.ps1' = 'e251ec832018846bffb08d662b9b41a71aea2b93'
        '02-Compilation/generate_release_docs_v4327.py' = 'fe0ec0f14bb250a34e2f229117d417dde2de651c'
        '02-Compilation/package_cumulative_release_v4327.py' = 'fa16ae7318ea72fc6485034a28a0943119189aef'
        '02-Compilation/release_document_guard_v4327.py' = 'c48b85da6ef40039fc851e06362456e1b439d568'
        '02-Compilation/installer/OpenVisio-V43.27-Candidate.iss' = 'd9a097349a7d91b19c55bbd6ca984b59b71f5d14'
        '.github/workflows/openvisio-v43.27-windows-candidate.yml' = '2e42c0bc960ea4b700db08ba4a186332807661e4'
        '02-Compilation/requirements-build.txt' = '23feee4dfbc0ba8ee8e1c2062ea083ed5bf9d6c7'
        '02-Compilation/verify_release_archive.py' = 'e5a2b76054f26c7c1b91e50316da7a9788301878'
        '02-Compilation/verify_release_git_parity.py' = 'bc0feeb9decaa6d74ccb0e35cb363919535ba9d8'
        '02-Compilation/verify_release_git_parity_v4327.py' = '04b86831047aa96a151bc82012ae25717da5b7bd'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
        '.gitattributes' = 'a373238348b68914c446bd3473e804a5d0897378'
        '04-Tests/Smoke-Portable-V42.71.ps1' = '5c4e7488e07629cf2386c54ed54d5c24f89b7d1d'
        '04-Tests/Smoke-Installer-V42.71.ps1' = '6adb9f52ed925286fc31a85360886519e2a2ae9f'
        '05-Documentation/V43.27-FORMULA-DRIVEN-VSDX-GEOMETRY.md' = '0a3732864e12c3bbb336f44ed3563707f7398ff2'
        '05-Documentation/V43.27-FORMULA-GEOMETRY-FIDELITY.svg' = '462f3bec8c22633ce75e03c0072fbce5d8eab8bc'
        '05-Documentation/V43.27-WINDOWS-SCREENSHOTS-STATUS.md' = '034f60e3dde2608cb38a8da49fc55ca2c7d7bb34'
        '05-Documentation/V43.27-SHAPESHEET-REFERENCE-CASEFOLD.md' = 'da704be81b44539e5447ecadd2123af90ec5d078'
        'README.md' = 'cf4e7164c39bc0fa4f9a7a0d917969f8495937ed'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing pinned file: $path" }
        $actual = (@(git rev-parse "HEAD:$path") -join '').Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) {
            throw "Git blob mismatch: $path (expected $($expected[$path]), got $actual)"
        }
    }
    $status = (@(git status --porcelain) -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $status) { throw "Independent checkout not clean: $status" }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Mirror source/test parity failed' }
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.27 --json-report (Join-Path $env:TEMP 'OpenVisio-V43.27-independent-checkout-audit.json')
    if ($LASTEXITCODE -ne 0) { throw 'Independent checkout archive/source gate failed' }
    python -m unittest discover -s python/tests -p 'test_vsdx_formula_geometry_fidelity_v4327.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'V43.27 formula geometry integration regressions failed' }
    python -m unittest discover -s python/tests -p 'test_visio_formula_v4327.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'V43.27 bounded parser unit tests failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Full Python suite failed in the independent checkout' }
    Write-Host "PASS exact independent checkout $head; $($expected.Count) Git blobs pinned; clean worktree; mirrors and full suite passed"
} finally {
    Pop-Location
}
