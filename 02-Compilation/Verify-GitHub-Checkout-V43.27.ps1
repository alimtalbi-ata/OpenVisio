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
        '03-Sources/openvisio/vsdx.py' = 'cbaccb58095ac6e08ad159002d20b39d15bcba33'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/routing.py' = 'b830d2e142c16b285e5057f9398fea31e99ea832'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        '03-Sources/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        '03-Sources/openvisio/vsdx_external.py' = 'e918cab7e5f92e6c522b35c868f377a8f7451559'
        '03-Sources/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        '03-Sources/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        '03-Sources/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        '03-Sources/openvisio/vsdx_geometry.py' = 'e89c85c50d05ffb66739aa2245ca8ae817dd25a4'
        '03-Sources/openvisio/app.py' = '145dadc50d1e03f856b63f5d0392fae5d4733016'
        '03-Sources/openvisio/export.py' = 'b376736830a1ee6b9cd8720d6f349528600a8d7a'
        '03-Sources/openvisio/shape_icons.py' = '798ae65b9f23c8b92632f59cf002f63ca95b44de'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/vsdx.py' = 'cbaccb58095ac6e08ad159002d20b39d15bcba33'
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/routing.py' = 'b830d2e142c16b285e5057f9398fea31e99ea832'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        'python/openvisio/vsdx_external.py' = 'e918cab7e5f92e6c522b35c868f377a8f7451559'
        'python/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        'python/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        'python/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        'python/openvisio/vsdx_geometry.py' = 'e89c85c50d05ffb66739aa2245ca8ae817dd25a4'
        'python/openvisio/app.py' = '145dadc50d1e03f856b63f5d0392fae5d4733016'
        'python/openvisio/export.py' = 'b376736830a1ee6b9cd8720d6f349528600a8d7a'
        'python/openvisio/shape_icons.py' = '798ae65b9f23c8b92632f59cf002f63ca95b44de'
        'python/tests/test_vsdx_formula_geometry_fidelity_v4327.py' = '9241e29c6f0e26e2f764b0efc0492363e161551a'
        '04-Tests/tests/test_vsdx_formula_geometry_fidelity_v4327.py' = '9241e29c6f0e26e2f764b0efc0492363e161551a'
        'python/tests/test_vsdx_route_spatial_prefilter_v4325.py' = 'c413b3178c1a65dfa5dbd012bf017ff3a75b54d7'
        '04-Tests/tests/test_vsdx_route_spatial_prefilter_v4325.py' = 'c413b3178c1a65dfa5dbd012bf017ff3a75b54d7'
        'python/tests/test_vsdx_route_segment_prefilter_v4325.py' = '63a0cc6af4c56d2d0e721e5298acc7842e538d15'
        '04-Tests/tests/test_vsdx_route_segment_prefilter_v4325.py' = '63a0cc6af4c56d2d0e721e5298acc7842e538d15'
        '02-Compilation/Build-Windows-V43.27-Candidate.ps1' = '09a86affc7baeb64894e07a3d62d403072db64f5'
        '02-Compilation/generate_release_docs_v4327.py' = '821fae53bdf6129a2a0e92c1db4002830a2f4d53'
        '02-Compilation/package_cumulative_release_v4327.py' = 'fc1649f2a5f37189e40531c989a79480c17eef05'
        '02-Compilation/release_document_guard_v4327.py' = 'f01fbc79f0c31f99726b4b64aa9db9e6407c6a56'
        '02-Compilation/installer/OpenVisio-V43.27-Candidate.iss' = 'd9a097349a7d91b19c55bbd6ca984b59b71f5d14'
        '.github/workflows/openvisio-v43.27-windows-candidate.yml' = 'b535ded9784beed1c2d2dc7e11456c6a83de3521'
        '02-Compilation/requirements-build.txt' = '23feee4dfbc0ba8ee8e1c2062ea083ed5bf9d6c7'
        '02-Compilation/verify_release_archive.py' = 'e5a2b76054f26c7c1b91e50316da7a9788301878'
        '02-Compilation/verify_release_git_parity.py' = 'bc0feeb9decaa6d74ccb0e35cb363919535ba9d8'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
        '.gitattributes' = 'a373238348b68914c446bd3473e804a5d0897378'
        '04-Tests/Smoke-Portable-V42.71.ps1' = '5c4e7488e07629cf2386c54ed54d5c24f89b7d1d'
        '04-Tests/Smoke-Installer-V42.71.ps1' = '6adb9f52ed925286fc31a85360886519e2a2ae9f'
        '05-Documentation/V43.27-FORMULA-DRIVEN-VSDX-GEOMETRY.md' = '13b7e342572a4d18b9b64d0cc86231a7b077c5e0'
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
    if ($LASTEXITCODE -ne 0) { throw 'V43.27 formula geometry targeted regressions failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Full Python suite failed in the independent checkout' }
    Write-Host "PASS exact independent checkout $head; $($expected.Count) Git blobs pinned; clean worktree; mirrors and full suite passed"
} finally {
    Pop-Location
}
