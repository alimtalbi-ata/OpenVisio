# OpenVisio V43.23 independent GitHub checkout and critical Git blob verification.
# Author: Abdelhalim Talbi. Candidate only; no production changes.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4323-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.23-static-vsdx-routes-and-canonical-payload-20261026'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) { throw "Destination must not exist: $Destination" }
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'Independent GitHub checkout failed' }
Push-Location $Destination
try {
    $head = (@(git rev-parse HEAD) -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $head -notmatch '^[0-9a-f]{40}$') { throw 'Cannot resolve independent checkout HEAD' }
    if ($env:OPENVISIO_EXPECTED_SOURCE_SHA -and $head -ne $env:OPENVISIO_EXPECTED_SOURCE_SHA) {
        throw "Independent checkout $head differs from selected CI source $env:OPENVISIO_EXPECTED_SOURCE_SHA"
    }
    $expected = @{
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/routing.py' = 'f76d9d1f2e93e2ac1635a0ed801ef173800ceb72'
        '03-Sources/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        '03-Sources/openvisio/vsdx_external.py' = 'd4cac43468c1e41f7c19cfb78536219c795a324d'
        '03-Sources/openvisio/visio_route.py' = 'b13c540e2a30903742c7b325cc29b1efae94e7d4'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        '03-Sources/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        '03-Sources/openvisio/vsdx_polyline.py' = 'd884e1caf27686154ec8e6d60588fad84e42308d'
        '03-Sources/openvisio/connector_geometry.py' = '62809851434f39e787e62c97344f7fb3055c448c'
        '03-Sources/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        '03-Sources/openvisio/geometry_lock.py' = '4905c6cbbe8e94a2f06a84491457baea48570a78'
        '03-Sources/openvisio/san_multipath.py' = 'd3143bd756528082add0fa3d1efeb9e4165eecc1'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/routing.py' = 'f76d9d1f2e93e2ac1635a0ed801ef173800ceb72'
        'python/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        'python/openvisio/vsdx_external.py' = 'd4cac43468c1e41f7c19cfb78536219c795a324d'
        'python/openvisio/visio_route.py' = 'b13c540e2a30903742c7b325cc29b1efae94e7d4'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/vsdx_package.py' = 'a32b0c21b00a2d3c220644d5db67d015ca0b521c'
        'python/openvisio/vsdx_polyline.py' = 'd884e1caf27686154ec8e6d60588fad84e42308d'
        'python/openvisio/connector_geometry.py' = '62809851434f39e787e62c97344f7fb3055c448c'
        'python/openvisio/node_geometry.py' = 'd14a6b5fc2b4d36247ad23d3b0a8dbb83eb43275'
        'python/openvisio/geometry_lock.py' = '4905c6cbbe8e94a2f06a84491457baea48570a78'
        'python/openvisio/san_multipath.py' = 'd3143bd756528082add0fa3d1efeb9e4165eecc1'
        '04-Tests/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        'python/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        '04-Tests/tests/test_vsdx_embedded_part_canonical_v4322.py' = '3b7e1fb59e284c91a6bf2e39f52ff803dff89669'
        'python/tests/test_vsdx_embedded_part_canonical_v4322.py' = '3b7e1fb59e284c91a6bf2e39f52ff803dff89669'
        '04-Tests/tests/test_vsdx_external_orthogonal_v4315.py' = '8969bd089088bb8fb2ee8bad19afe3992071cb25'
        'python/tests/test_vsdx_external_orthogonal_v4315.py' = '8969bd089088bb8fb2ee8bad19afe3992071cb25'
        '04-Tests/tests/test_vsdx_static_route_preservation_v4322.py' = 'aa72240de6063a151be269ad33d12c685a9856ad'
        'python/tests/test_vsdx_static_route_preservation_v4322.py' = 'aa72240de6063a151be269ad33d12c685a9856ad'
        '04-Tests/tests/test_release_archive_guard_v4320.py' = '4094511b54ea6a4b695f4101abcc451953ce8db3'
        '02-Compilation/verify_release_archive.py' = 'e5a2b76054f26c7c1b91e50316da7a9788301878'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
        '.gitattributes' = 'a9b945c66de7ab90436001ee76aafe91a22ee20f'
        '02-Compilation/Build-Windows-V43.23-Candidate.ps1' = 'e89ea32c2372ba89d947172fee18dd548467ff36'
        '02-Compilation/generate_release_docs_v4323.py' = 'cf07ca16a66db07b4bdeb2d0533f66ed304d7da1'
        '02-Compilation/package_cumulative_release_v4323.py' = 'bdebef4de9ec9be031a07d0a48f7d8ef5386ddcc'
        '02-Compilation/release_document_guard_v4323.py' = '62ce7295c71e419add52fdb31ce115d6aea647aa'
        '02-Compilation/installer/OpenVisio-V43.23-Candidate.iss' = '02f473a82c8c29adf6adb104e9a552b79a07e432'
        '.github/workflows/openvisio-v43.23-windows-candidate.yml' = '5a1914b79d2a5567f6a164aedea6085c9478601a'
        'README.md' = '2b4288c644e7ac0d00b685f276742a88be9fb376'
        '05-Documentation/V43.23-STATIC-VSDX-WAYPOINTS.md' = '367003f6f4093cf883a1537ed0706078fcef1e03'
        '05-Documentation/V43.23-STATIC-VSDX-WAYPOINTS.svg' = 'c57f75add5b6893aa4c679a65a7dacf156816017'
        '05-Documentation/V43.23-INTEGRATED-ROUTES.md' = 'e182af1f02a1b76d7ecc06cbabef47c91c12806b'
        '05-Documentation/V43.23-WINDOWS-SCREENSHOTS-STATUS.md' = 'a63a42bcfb93904a2b4eb7e36a1e2e9b76941319'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing critical file: $path" }
        $actual = (@(git rev-parse "HEAD:$path") -join '').Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) { throw "Git blob mismatch: $path (expected $($expected[$path]), got $actual)" }
    }
    $status = (@(git status --porcelain) -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $status) { throw "Independent checkout not clean: $status" }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source/test mirror parity failed' }
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.23 --json-report (Join-Path $Destination 'dist/V43.23-independent-checkout-audit.json')
    if ($LASTEXITCODE -ne 0) { throw 'Source/release checkout validation failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Full Python suite failed from independent checkout' }
    Write-Host "PASS independent checkout $head; $($expected.Count) critical blobs pinned; clean worktree; mirror parity; full Python suite"
} finally { Pop-Location }
