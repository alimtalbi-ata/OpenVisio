# V43.22 independent GitHub checkout, critical Git blob pins, mirror parity, and test gate.
# Author: Abdelhalim Talbi. Candidate only; no production changes.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4322-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.22-vsdx-private-part-case-guard-20261026'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) { throw "Destination must not exist: $Destination" }
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'Independent GitHub checkout failed' }
Push-Location $Destination
try {
    $head = (@(git rev-parse HEAD) -join '').Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve independent checkout HEAD' }
    if ($env:OPENVISIO_EXPECTED_SOURCE_SHA -and $head -ne $env:OPENVISIO_EXPECTED_SOURCE_SHA) {
        throw "Independent checkout $head differs from selected CI source $env:OPENVISIO_EXPECTED_SOURCE_SHA"
    }
    $expected = @{
        '03-Sources/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        'python/openvisio/model.py' = 'e4d0a90ba71f6237a1597c1318aac165db242016'
        '03-Sources/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        'python/openvisio/render.py' = '7732416abb88f7adbdb64b8ea05c185ab029b5e1'
        '03-Sources/openvisio/routing.py' = '15de75b0b4db520e92ca6d1df0e273ed022b607a'
        'python/openvisio/routing.py' = '15de75b0b4db520e92ca6d1df0e273ed022b607a'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        '04-Tests/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        '03-Sources/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        'python/openvisio/vsdx.py' = '30d99082c90de6b11a3626a28ca20797ecc60e97'
        'python/tests/test_vsdx_embedded_part_canonical_v4322.py' = '3b7e1fb59e284c91a6bf2e39f52ff803dff89669'
        '04-Tests/tests/test_vsdx_embedded_part_canonical_v4322.py' = '3b7e1fb59e284c91a6bf2e39f52ff803dff89669'
        '02-Compilation/Build-Windows-V43.22-Candidate.ps1' = '3197f3762854fefd53ae4d12a853a6ad9d0b5175'
        '02-Compilation/generate_release_docs_v4322.py' = '039a6aced876ee5ce85583260fa21f45f2200542'
        '02-Compilation/package_cumulative_release_v4322.py' = 'e42aa86e3bfbb28551b63933921aad18bc3e7f59'
        '02-Compilation/installer/OpenVisio-V43.22-Candidate.iss' = '809dc3e61ef1631a5d57b0905f33feede0b6ef22'
        '02-Compilation/release_document_guard_v4322.py' = '13005665678b2e601fd5eb54d313792d725e725a'
        '05-Documentation/V43.22-VSDX-PRIVATE-PARTS.md' = '89efcc8c785837b39c79b1c31eb05db45bc26261'
        '05-Documentation/V43.22-VSDX-PRIVATE-PARTS.svg' = '39a440337d82cac6d58fc01a361a699a01b1c311'
        '05-Documentation/V43.22-WINDOWS-SCREENSHOTS-STATUS.md' = '08dd6707da1d249a761f18011b5cbcf76be246ee'
        '.github/workflows/openvisio-v43.22-windows-candidate.yml' = 'fe64328ad95cac47a6291dcc877d168fea85495a'
        '.gitattributes' = 'a9b945c66de7ab90436001ee76aafe91a22ee20f'
        '02-Compilation/verify_release_archive.py' = 'e5a2b76054f26c7c1b91e50316da7a9788301878'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing critical source: $path" }
        $actual = (@(git rev-parse "HEAD:$path") -join '').Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) { throw "Git blob mismatch: $path" }
    }
    $status = (@(git status --porcelain) -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $status) { throw "Independent checkout not clean: $status" }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Mirrored source/test parity failed' }
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.22
    if ($LASTEXITCODE -ne 0) { throw 'Source/release checkout gate failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Full Python suite failed from independent checkout' }
    Write-Host "PASS independent checkout $head; pinned source/test/docs/workflow blobs; mirror parity; full test suite"
} finally { Pop-Location }
