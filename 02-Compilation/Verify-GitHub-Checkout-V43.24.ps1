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
