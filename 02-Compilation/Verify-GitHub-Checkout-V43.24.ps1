# OpenVisio V43.24 independent checkout and source-pinning gate.
# Uses the exact commit selected by GitHub Actions; no secrets or production access.
# Author: Abdelhalim Talbi.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP ('openvisio-v4324-independent-' + [guid]::NewGuid().ToString('N'))))
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
        '03-Sources/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/visio_route.py' = '7b76ca1b300baa5a24fd45514cc12e5ff83bce07'
        '04-Tests/tests/test_vsdx_route_endpoint_attachment_v4324.py' = '7e48620355d8516fb8863d5983b62b960df84fc4'
        'python/tests/test_vsdx_route_endpoint_attachment_v4324.py' = '7e48620355d8516fb8863d5983b62b960df84fc4'
        '02-Compilation/verify_release_archive.py' = 'e5a2b76054f26c7c1b91e50316da7a9788301878'
        '02-Compilation/verify_release_git_parity.py' = '279f809dc099ae824f5562ed44adfaf2c1d403f0'
        '02-Compilation/Build-Windows-V43.24-Candidate.ps1' = '2a2dedd8092d039463326e46b5f231793d227023'
        '02-Compilation/package_cumulative_release_v4324.py' = '2320daf68716c4bff956d511e353a1e166dc697d'
        '02-Compilation/generate_release_docs_v4324.py' = 'ef8613a203e352c091cd8a1ae8c300c7db4fde29'
        '02-Compilation/release_document_guard_v4324.py' = 'b2f08359e0948ac3f4a8118d423c869e2d20f50a'
        '02-Compilation/installer/OpenVisio-V43.24-Candidate.iss' = '85c5d3a56c5592eba0b4a3caa97d13516bbe34b0'
        '04-Tests/tests/test_release_git_parity_v4324.py' = 'e6ef32c10ab3d49f9e6e8f2a611b73501dbe9132'
        'python/tests/test_release_git_parity_v4324.py' = 'e6ef32c10ab3d49f9e6e8f2a611b73501dbe9132'
        '05-Documentation/V43.24-GIT-BLOB-PARITY.md' = 'e844e6af1a0b0a67b3cfb7d5c0936fb5c7392205'
        '05-Documentation/V43.24-STATIC-VSDX-ROUTE-ATTACHMENT.md' = '9ea8ae90a3720310e3b34391fc4503c6b38a88c2'
        '05-Documentation/V43.24-VSDX-ENDPOINT-ATTACHMENT.svg' = '6320c1a451561b5cd840956f7b2806055cb92bbf'
        '.gitattributes' = '9eaad06937c9c364b583c7bdff26511640c2d7f9'
        '.github/workflows/openvisio-v43.24-windows-candidate.yml' = '7c1c0ef032df9a22e59da0263ae7c62fc6c775be'
        '02-Compilation/verify_release_git_parity.py' = '279f809dc099ae824f5562ed44adfaf2c1d403f0'
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
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.24 --json-report (Join-Path $Destination 'v43.24-independent-checkout-audit.json')
    if ($LASTEXITCODE -ne 0) { throw 'Independent checkout archive/source gate failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Full Python suite failed in the independent checkout' }
    Write-Host "PASS exact independent checkout $head; critical engine/test blobs pinned; clean worktree; parity and complete suite passed"
} finally {
    Pop-Location
}
