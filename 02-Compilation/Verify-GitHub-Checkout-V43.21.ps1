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
        '03-Sources/openvisio/routing.py' = '15de75b0b4db520e92ca6d1df0e273ed022b607a'
        'python/openvisio/routing.py' = '15de75b0b4db520e92ca6d1df0e273ed022b607a'
        '03-Sources/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/openvisio/parallel_geometry.py' = '74776b436e0c6425eda4bc44fb060c8ab1e878f9'
        'python/tests/test_low_zoom_label_lod_v4320.py' = 'f27363d69717142015065ea5613a34d769704d05'
        '04-Tests/tests/test_low_zoom_label_lod_v4320.py' = 'f27363d69717142015065ea5613a34d769704d05'
        'python/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '04-Tests/tests/test_node_label_fidelity_v4319.py' = 'cddaeba6bbd23c325c251d89e4b69953bb2f1c8b'
        '02-Compilation/verify_release_archive.py' = 'e5a2b76054f26c7c1b91e50316da7a9788301878'
        'python/tests/test_release_archive_guard_v4320.py' = '4094511b54ea6a4b695f4101abcc451953ce8db3'
        '04-Tests/tests/test_release_archive_guard_v4320.py' = '4094511b54ea6a4b695f4101abcc451953ce8db3'
        'python/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        '04-Tests/tests/test_vsdx_zip_path_canonical_v4321.py' = 'f53f2c2405fa97e7494200fa31417c88b795eb1e'
        '02-Compilation/Build-Windows-V43.21-Candidate.ps1' = '042efd09096cfdfdee7c97a0390ac207d0905937'
        '02-Compilation/generate_release_docs_v4321.py' = '43abf3a2a7fcd967a603d18fe886b1c295b42dcf'
        '02-Compilation/release_document_guard.py' = '0439f3ae1e6b403fcf5d0ebaa5b9821f0ac8d11f'
        'python/tests/test_release_document_guard_v4321.py' = 'ce38a34fcafe28557efba60a9f3fbe4878815ee9'
        '04-Tests/tests/test_release_document_guard_v4321.py' = 'ce38a34fcafe28557efba60a9f3fbe4878815ee9'
        '02-Compilation/package_cumulative_release_v4321.py' = '6193df5d6c2483e714ed01180fcbd269566c2ce4'
        '02-Compilation/requirements-build.txt' = '23feee4dfbc0ba8ee8e1c2062ea083ed5bf9d6c7'
        '02-Compilation/installer/OpenVisio-V43.21-Candidate.iss' = '463597406eded285759c11f8b2ffbdbe4b12402e'
        'README.md' = '6a492a7489236d4990d7e00e378dc7f3bccddd13'
        '05-Documentation/V43.21-CANONICAL-PATHS.md' = '6577c11eb0b01b4fdf3256fa9fe71f86465e601f'
        '05-Documentation/V43.21-CANONICAL-PATHS.svg' = 'ced9ec833ba56b19ac45751a070972d6ef2972c9'
        '05-Documentation/V43.21-WINDOWS-SCREENSHOTS-STATUS.md' = '66f504a440fb108d6310ae0fd9eb6f6249de2107'
        '.github/workflows/openvisio-v43.21-windows-candidate.yml' = '937b90dc9216b4b17a6ba0c7e7583ae21ffb2c53'
        'verify_source_parity.py' = '7b392e310452c37c26f4f254f2860fbea4f7dbae'
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
    python 02-Compilation/verify_release_archive.py --checkout $Destination --version V43.21
    if ($LASTEXITCODE -ne 0) { throw 'Cumulative release source guard failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent checkout $head, critical engine blob identities, mirror parity, and complete Python suite"
} finally { Pop-Location }
