# V43.22 independent GitHub checkout, engine SHA, mirror parity, and test gate.
# Author: Abdelhalim Talbi. Candidate only; never modifies main.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4322-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.22-static-vsdx-waypoints-20261025'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) { throw "Destination must not exist: $Destination" }
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'Independent checkout failed' }
Push-Location $Destination
try {
    $head = (@(git rev-parse HEAD) -join '').Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve checkout HEAD' }
    if ($env:OPENVISIO_EXPECTED_SOURCE_SHA -and $head -ne $env:OPENVISIO_EXPECTED_SOURCE_SHA) { throw "Independent branch checkout $head differs from expected source SHA $env:OPENVISIO_EXPECTED_SOURCE_SHA" }
    $expected = @{
        '.gitattributes' = 'a9b945c66de7ab90436001ee76aafe91a22ee20f'
        '.github/workflows/openvisio-v42.93-windows-candidate.yml' = '55288f90e8d346dcbd0eb7c3c57eedf8a6eb1b00'
        '.github/workflows/openvisio-v42.94-windows-candidate.yml' = '35a29947cea355c9e81a8f1ad0bdd3ea10f14d97'
        '04-Tests/Smoke-Portable-V42.71.ps1' = '5c4e7488e07629cf2386c54ed54d5c24f89b7d1d'
        '04-Tests/Smoke-Installer-V42.71.ps1' = '6adb9f52ed925286fc31a85360886519e2a2ae9f'
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/vsdx.py' = '31003ad2220fe46769858e5724f5150235b2d5a0'
        'python/openvisio/vsdx.py' = '31003ad2220fe46769858e5724f5150235b2d5a0'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/routing.py' = 'f76d9d1f2e93e2ac1635a0ed801ef173800ceb72'
        'python/openvisio/routing.py' = 'f76d9d1f2e93e2ac1635a0ed801ef173800ceb72'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/tests/test_low_zoom_label_lod_v4320.py' = 'f27363d69717142015065ea5613a34d769704d05'
        '04-Tests/tests/test_low_zoom_label_lod_v4320.py' = 'f27363d69717142015065ea5613a34d769704d05'
        'python/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '04-Tests/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '02-Compilation/verify_release_archive.py' = 'c6c9fff724157d050f8b8c71509024bb7609bffd'
        'python/tests/test_release_archive_guard_v4320.py' = '5d108df4c7a9efbddd0048b36ec06d1a219bdfc3'
        '04-Tests/tests/test_release_archive_guard_v4320.py' = '5d108df4c7a9efbddd0048b36ec06d1a219bdfc3'
        'python/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        '04-Tests/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        '02-Compilation/Build-Windows-V43.22-Candidate.ps1' = '833823afc3771adec243cd12fedd52d1c08db854'
        '02-Compilation/generate_release_docs_v4322.py' = 'd938d1538209c7a4c00a34344c59c599661e35c8'
        '02-Compilation/release_document_guard.py' = '0439f3ae1e6b403fcf5d0ebaa5b9821f0ac8d11f'
        'python/tests/test_release_document_guard_v4322.py' = '37b1895b182568225185ccf0238093de4310ac4d'
        '04-Tests/tests/test_release_document_guard_v4322.py' = '37b1895b182568225185ccf0238093de4310ac4d'
        '02-Compilation/package_cumulative_release_v4322.py' = 'a44ff881f8b09c147e0be015b69db81e8f237358'
        '02-Compilation/requirements-build.txt' = '23feee4dfbc0ba8ee8e1c2062ea083ed5bf9d6c7'
        '02-Compilation/installer/OpenVisio-V43.22-Candidate.iss' = '809dc3e61ef1631a5d57b0905f33feede0b6ef22'
        'README.md' = 'fede2366c92ad8908f16a0fdb7886d1725e1db47'
        '05-Documentation/V43.22-STATIC-VSDX-WAYPOINTS.md' = 'fefd5f12664ba07494045853b1a5cf61af1cc683'
        '05-Documentation/V43.22-STATIC-VSDX-WAYPOINTS.svg' = '66f38d78cfaebb31d8773ddf55f9796be0b10c2a'
        '05-Documentation/V43.22-WINDOWS-SCREENSHOTS-STATUS.md' = '1bab469ae5d314e873ec5bd29ab5114de5e69367'
        '.github/workflows/openvisio-v43.22-windows-candidate.yml' = '74377906e8d068a1809861715ff2183ffb06cf2a'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
        '02-Compilation/release_document_guard_v4322.py' = '13005665678b2e601fd5eb54d313792d725e725a'
        '03-Sources/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        '03-Sources/openvisio/visio_route.py' = 'b13c540e2a30903742c7b325cc29b1efae94e7d4'
        '03-Sources/openvisio/vsdx_external.py' = 'd4cac43468c1e41f7c19cfb78536219c795a324d'
        '04-Tests/tests/test_vsdx_external_orthogonal_v4315.py' = '8969bd089088bb8fb2ee8bad19afe3992071cb25'
        '04-Tests/tests/test_vsdx_static_route_preservation_v4322.py' = 'aa72240de6063a151be269ad33d12c685a9856ad'
        'python/openvisio/validation.py' = '01af42939e84f9b94e7877ae88bac373c0b055e2'
        'python/openvisio/visio_route.py' = 'b13c540e2a30903742c7b325cc29b1efae94e7d4'
        'python/openvisio/vsdx_external.py' = 'd4cac43468c1e41f7c19cfb78536219c795a324d'
        'python/tests/test_vsdx_external_orthogonal_v4315.py' = '8969bd089088bb8fb2ee8bad19afe3992071cb25'
        'python/tests/test_vsdx_static_route_preservation_v4322.py' = 'aa72240de6063a151be269ad33d12c685a9856ad'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing critical source: $path" }
        $actual = (@(git rev-parse "HEAD:$path") -join '').Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) { throw "Git blob mismatch: $path expected $($expected[$path]) got $actual" }
    }
    $status = (@(git status --porcelain) -join '').Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect checkout status' }
    if ($status) { throw "Checkout is not clean: $status" }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source/test mirror parity failed' }
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.22
    if ($LASTEXITCODE -ne 0) { throw 'Cumulative release source guard failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent checkout $head, critical engine blob identities, mirror parity, and complete Python suite"
} finally { Pop-Location }
