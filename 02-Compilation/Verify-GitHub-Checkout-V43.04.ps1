# Reproducible independent checkout of the OpenVisio V43.04 candidate.
# Author: Abdelhalim Talbi. Does not modify main or production.
[CmdletBinding()]
param([string]$Destination = (Join-Path $env:TEMP 'openvisio-v4304-verify'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'develop/v43.04-clickable-san-connector-captions-20261024'
$repo = 'https://github.com/alimtalbi-ata/OpenVisio.git'
if (Test-Path -LiteralPath $Destination) {
    throw "Destination must not exist; choose an empty path: $Destination"
}
git clone --single-branch --branch $branch --depth 1 $repo $Destination
if ($LASTEXITCODE -ne 0) { throw 'GitHub checkout failed' }
Push-Location $Destination
try {
    $head = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve checkout HEAD' }
    if ($env:GITHUB_SHA -and $head -ne $env:GITHUB_SHA) {
        throw "Independent checkout $head differs from workflow commit $env:GITHUB_SHA"
    }
    $expected = @{
        'python/openvisio/vsdx_package.py' = '1b1db6b86b9065e19162195cd58ad0122adcf1a6'
        'python/openvisio/vsdx_fidelity.py' = 'c1c7ad8117b14acb3ae30604864c0fa0111063eb'
        'python/tests/test_vsdx_xml10_captions_v4300.py' = 'c89af2bdcc0cf451bfee1b1361df44f40066af5c'
        '04-Tests/tests/test_vsdx_xml10_captions_v4300.py' = 'c89af2bdcc0cf451bfee1b1361df44f40066af5c'
        'python/openvisio/vsdx_external.py' = 'd2bd08fe54fd3a5a5a3da79b3f4aae8ca5dcf955'
        '03-Sources/openvisio/vsdx_external.py' = 'd2bd08fe54fd3a5a5a3da79b3f4aae8ca5dcf955'
        'python/tests/test_vsdx_page_part_identity_v4301.py' = '8756498c6cf9d04717c0b5ff19b647eeedd33ee4'
        '04-Tests/tests/test_vsdx_page_part_identity_v4301.py' = '8756498c6cf9d04717c0b5ff19b647eeedd33ee4'
        'python/tests/test_vsdx_dual_name_identity_v4303.py' = '42aec5d0f6c701352a320c0be87132bbb45a9838'
        '04-Tests/tests/test_vsdx_dual_name_identity_v4303.py' = '42aec5d0f6c701352a320c0be87132bbb45a9838'
        'python/openvisio/model.py' = '747522deae7dbd5eee321726cc2df2095f9f7601'
        'python/openvisio/vsdx.py' = '0f5d8f4d2b0f23bef065d4700e0487a6b45a9af6'
        'python/tests/test_connector_label_hit_v4304.py' = 'c4c690b6fb5bb0371e6eabc25830e20e9aa89ff8'
        '04-Tests/tests/test_connector_label_hit_v4304.py' = 'c4c690b6fb5bb0371e6eabc25830e20e9aa89ff8'
        'python/tests/test_parallel_hit_priority_v4277.py' = 'bce9a9e8078ec527bfb14981c07f4b8c85e2b638'
        '04-Tests/tests/test_parallel_hit_priority_v4277.py' = 'bce9a9e8078ec527bfb14981c07f4b8c85e2b638'
        'python/openvisio/render.py' = 'cb279babf77ea3d0fa8860f4717b53fc00f36bb8'
        'python/openvisio/export.py' = '88d4d2ffddc1ca25e8209b6c945649f4d8ae8179'
        'python/openvisio/retained_canvas.py' = '5c2d81ba7def18a00f6bf2a7f0b3d6dd047c04bf'
        'python/openvisio/shape_icons.py' = '4dc8bb45938f6908af09fa4c0045e89e244205f4'
        'python/openvisio/connector_labels.py' = '3740ae616d608ad15b9d851ebc067ba8656a376d'
        'python/openvisio/app.py' = 'b9fe39769387b87198e12319f65893f9d89ed521'
        'python/openvisio/commands.py' = '1036c435e0b91355469510f741cfea95f3a87796'
        'python/tests/test_san_parallel_fabric_layer_v4295.py' = 'e56da80b12edc4bbd1f79dbcea7135cc59985035'
        'python/tests/test_svg_layer_visibility_v4296.py' = 'b51176e999fb689eda282680cf8ff674198cecb4'
        'python/tests/test_svg_atomic_export_v4298.py' = 'b0ab6e2b9cb4231eb088eb8f80412397311ec7e7'
        'python/tests/test_svg_dimension_integrity_v4297.py' = '1c58f2faab5c2313acd8a23b310413fedda6a510'
        'python/tests/test_svg_xml10_integrity_v4299.py' = '5b2d34d94f38b871fd7d7e9ff0792e164ca28924'
        'python/tests/test_connector_null_metadata_v4294.py' = 'd996a948d51ded222d38cf46bdd82154d0872348'
        'python/tests/test_vsdx_vendor_san_identity_v4302.py' = '26712b957039f5ab9a87e7a07fd344edf0c48ff8'
        '04-Tests/tests/test_vsdx_vendor_san_identity_v4302.py' = '26712b957039f5ab9a87e7a07fd344edf0c48ff8'
    }
    foreach ($path in $expected.Keys) {
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Critical checkout file missing: $path"
        }
        $actual = (git hash-object -- $path).Trim()
        if ($LASTEXITCODE -ne 0 -or $actual -ne $expected[$path]) {
            throw "Git blob mismatch: $path expected $($expected[$path]) got $actual"
        }
    }
    $env:PYTHONPATH = Join-Path $Destination 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Mirror parity failed' }
    python -m unittest discover -s python/tests -p 'test_*.py' -q
    if ($LASTEXITCODE -ne 0) { throw 'Python checkout tests failed' }
    Write-Host "PASS: independent GitHub checkout $head, critical engine SHA, mirrors and tests"
} finally {
    Pop-Location
}
