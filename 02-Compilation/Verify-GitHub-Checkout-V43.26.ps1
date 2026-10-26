# OpenVisio V43.26 independent checkout and source-pinning gate.
# Uses the exact commit selected by GitHub Actions; no secrets or production access.
# Author: Abdelhalim Talbi.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP ('openvisio-v4326-independent-' + [guid]::NewGuid().ToString('N'))))
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
        '.gitattributes' = 'a373238348b68914c446bd3473e804a5d0897378'
        'README.md' = 'ecc00212d38a1e96d3f75b6f2ff9f3707b5a5940'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        '03-Sources/openvisio/render.py' = '00684d57a7d12a9bd2a5777c395608c49022f014'
        '03-Sources/openvisio/export.py' = '4c920c1fae7bcb6fc166b7823b23d16f8cd94893'
        '03-Sources/openvisio/shape_icons.py' = '0146c26290de1b077ec02897eb5462b12147cb77'
        '03-Sources/openvisio/routing.py' = 'b830d2e142c16b285e5057f9398fea31e99ea832'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        '03-Sources/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        '03-Sources/openvisio/vsdx_external.py' = 'd4cac43468c1e41f7c19cfb78536219c795a324d'
        '03-Sources/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        '03-Sources/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        '03-Sources/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        'python/openvisio/render.py' = '00684d57a7d12a9bd2a5777c395608c49022f014'
        'python/openvisio/export.py' = '4c920c1fae7bcb6fc166b7823b23d16f8cd94893'
        'python/openvisio/shape_icons.py' = '0146c26290de1b077ec02897eb5462b12147cb77'
        'python/openvisio/routing.py' = 'b830d2e142c16b285e5057f9398fea31e99ea832'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        'python/openvisio/vsdx_external.py' = 'd4cac43468c1e41f7c19cfb78536219c795a324d'
        'python/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        'python/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        'python/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        '04-Tests/tests/test_vsdx_route_endpoint_attachment_v4324.py' = '7e48620355d8516fb8863d5983b62b960df84fc4'
        'python/tests/test_vsdx_route_endpoint_attachment_v4324.py' = '7e48620355d8516fb8863d5983b62b960df84fc4'
        '04-Tests/tests/test_vsdx_route_spatial_prefilter_v4325.py' = 'c413b3178c1a65dfa5dbd012bf017ff3a75b54d7'
        'python/tests/test_vsdx_route_spatial_prefilter_v4325.py' = 'c413b3178c1a65dfa5dbd012bf017ff3a75b54d7'
        '04-Tests/tests/test_vsdx_route_segment_prefilter_v4325.py' = '63a0cc6af4c56d2d0e721e5298acc7842e538d15'
        'python/tests/test_vsdx_route_segment_prefilter_v4325.py' = '63a0cc6af4c56d2d0e721e5298acc7842e538d15'
        '04-Tests/tests/test_shape_icons_v4292.py' = '13684c684d476ef0355613cafdb791b16fa98804'
        'python/tests/test_shape_icons_v4292.py' = '13684c684d476ef0355613cafdb791b16fa98804'
        '04-Tests/tests/test_infrastructure_glyph_details_v4326.py' = 'ca8884c8cd642f99d12eccc5f3ef939d2e449a83'
        'python/tests/test_infrastructure_glyph_details_v4326.py' = 'ca8884c8cd642f99d12eccc5f3ef939d2e449a83'
        '04-Tests/tests/test_release_git_parity_v4324.py' = 'e6ef32c10ab3d49f9e6e8f2a611b73501dbe9132'
        'python/tests/test_release_git_parity_v4324.py' = 'e6ef32c10ab3d49f9e6e8f2a611b73501dbe9132'
        '02-Compilation/verify_release_archive.py' = 'e5a2b76054f26c7c1b91e50316da7a9788301878'
        '02-Compilation/verify_release_git_parity.py' = 'f831d76bfb50f8634ba94f702238317baf52d257'
        '02-Compilation/Build-Windows-V43.26-Candidate.ps1' = '8f176868741a6bf242b4a53c8f76b3372a18bd9d'
        '02-Compilation/package_cumulative_release_v4326.py' = 'd50ca10f5d1d4f71c9f368dfaa70abf0564f53e5'
        '02-Compilation/generate_release_docs_v4326.py' = '91a86681ce07eaa1714b375c575c0aa2c0f35cb5'
        '02-Compilation/release_document_guard_v4326.py' = '7c8a34b69d5f1f6dc47ca2dab65aa61b998efa42'
        '02-Compilation/requirements-build.txt' = '23feee4dfbc0ba8ee8e1c2062ea083ed5bf9d6c7'
        '02-Compilation/installer/OpenVisio-V43.26-Candidate.iss' = 'c8b00db9be3554c555179fdfb0db7042e6e830a9'
        '.github/workflows/openvisio-v43.26-windows-candidate.yml' = 'a3be6cc623f45158294787554f9cc1d83c2f8a8d'
        '05-Documentation/V43.24-STATIC-VSDX-ROUTE-ATTACHMENT.md' = '9ea8ae90a3720310e3b34391fc4503c6b38a88c2'
        '05-Documentation/V43.24-VSDX-ENDPOINT-ATTACHMENT.svg' = '6320c1a451561b5cd840956f7b2806055cb92bbf'
        '05-Documentation/V43.25-GIT-BLOB-PARITY.md' = '3b0addcf3a9d819c58dee0b83598fa8106518cc5'
        '05-Documentation/V43.25-STATIC-VSDX-ROUTE-PREFILTER.md' = 'aa6a39f00212821a29192313f9dd33e01066a21c'
        '05-Documentation/V43.25-STATIC-VSDX-ROUTE-PREFILTER.svg' = '3ae1b81fc34d0b45fa46b8bae7cb0fda75962114'
        '05-Documentation/V43.25-WINDOWS-SCREENSHOTS-STATUS.md' = 'd65adad1829d072b268a4072063be3e6c5a69b95'
        '05-Documentation/V43.26-GIT-BLOB-PARITY.md' = 'bbab4337aee1c664ba1b5f2ec5ee6a57b875d50c'
        '05-Documentation/V43.26-INFRASTRUCTURE-GLYPHS.md' = 'a54f0aa55ee4a808c2aa8f9f11657a7bd386ac1f'
        '05-Documentation/V43.26-INFRASTRUCTURE-GLYPHS.svg' = 'c584cff39bbac5abb2db8d8e29240bb76552aa02'
        '05-Documentation/V43.26-WINDOWS-SCREENSHOTS-STATUS.md' = 'ae942b63e0e1b8787b066a707e82e70d3206846c'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing critical file: $path" }
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
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.26 --json-report (Join-Path $Destination 'v43.26-independent-checkout-audit.json')
    if ($LASTEXITCODE -ne 0) { throw 'Independent checkout archive/source gate failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Full Python suite failed in the independent checkout' }
    Write-Host "PASS exact independent checkout $head; critical engine/test blobs pinned; clean worktree; parity and complete suite passed"
} finally {
    Pop-Location
}
