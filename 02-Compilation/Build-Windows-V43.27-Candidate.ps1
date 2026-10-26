# OpenVisio V43.27 source candidate — native Windows x64 build and smoke.
# Internal application version remains 42.50.0 due to legacy build contracts.
# Candidate only: NOT a production release or Microsoft Visio certification.
# Author: Abdelhalim Talbi.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $root
try {
    $env:PYTHONPATH = Join-Path $root 'python'
    python verify_source_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Source mirrors differ' }
    python 02-Compilation/verify_release_archive.py --checkout $root --version V43.27 --json-report (Join-Path $root 'dist/V43.27-checkout-integrity.json')
    if ($LASTEXITCODE -ne 0) { throw 'Release/source archive integrity gate failed' }
    $testLogDir = Join-Path $root 'dist/test-logs'
    New-Item -ItemType Directory -Path $testLogDir -Force | Out-Null
    function Invoke-UnitPattern {
        param([string]$Pattern)
        $output = & python -m unittest discover -s python/tests -p $Pattern -q 2>&1
        $code = $LASTEXITCODE
        $text = (@($output) | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
        $safeName = ($Pattern -replace '[^A-Za-z0-9._-]', '_') + '.log'
        Set-Content -LiteralPath (Join-Path $testLogDir $safeName) -Value $text -Encoding utf8
        if ($code -ne 0) { Write-Host $text; throw "Regression failed: $Pattern" }
        Write-Host "PASS targeted regression: $Pattern"
    }
    $fullOutput = & python -m unittest discover -s python/tests -p 'test_*.py' -v 2>&1
    $fullExit = $LASTEXITCODE
    $fullText = (@($fullOutput) | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
    Set-Content -LiteralPath (Join-Path $testLogDir 'full-python-suite.log') -Value $fullText -Encoding utf8
    if ($fullExit -ne 0) { Write-Host $fullText; throw 'Python suite failed' }
    $runMatch = [regex]::Match($fullText, 'Ran\s+(\d+)\s+tests?\s+in\s+([\d.]+)s')
    $skipMatch = [regex]::Match($fullText, 'OK\s+\(skipped=(\d+)\)')
    if (!$runMatch.Success) { throw 'Unable to parse the complete Python unittest summary' }
    $unitCount = [int]$runMatch.Groups[1].Value
    $unitDuration = [double]$runMatch.Groups[2].Value
    $skipCount = if ($skipMatch.Success) { [int]$skipMatch.Groups[1].Value } else { 0 }
    Write-Host "PASS full Python suite: $unitCount tests; $skipCount skipped; $unitDuration seconds"

    Invoke-UnitPattern -Pattern 'test_release_archive_guard_v4320.py'
    Invoke-UnitPattern -Pattern 'test_vsdx_zip_path_canonical_v4321.py'
    Invoke-UnitPattern -Pattern 'test_vsdx_embedded_part_canonical_v4322.py'
    Invoke-UnitPattern -Pattern 'test_vsdx_static_route_preservation_v4322.py'
    Invoke-UnitPattern -Pattern 'test_vsdx_route_endpoint_attachment_v4324.py'
    Invoke-UnitPattern -Pattern 'test_vsdx_route_spatial_prefilter_v4325.py'
    Invoke-UnitPattern -Pattern 'test_vsdx_formula_geometry_fidelity_v4327.py'
    Invoke-UnitPattern -Pattern 'test_low_zoom_label_lod_v4320.py'
    # Exercise real Tk callbacks on the Windows runner, not only headless model tests.
    $env:OPENVISIO_GUI_TESTS = '1'
    try {
        Invoke-UnitPattern -Pattern 'test_scene_navigation_v4310.py'
        Invoke-UnitPattern -Pattern 'test_vsdx_shape_identity_v4311.py'
        Invoke-UnitPattern -Pattern 'test_vsdx_master_identity_v4312.py'
        Invoke-UnitPattern -Pattern 'test_vsdx_master_precedence_v4313.py'
        Invoke-UnitPattern -Pattern 'test_vsdx_y_anchor_connectors_v4314.py'
        Invoke-UnitPattern -Pattern 'test_vsdx_external_orthogonal_v4315.py'
        Invoke-UnitPattern -Pattern 'test_vsdx_connector_loss_v4316.py'
        Invoke-UnitPattern -Pattern 'test_svg_direction_v4317.py'
        Invoke-UnitPattern -Pattern 'test_svg_multiline_labels_v4318.py'
    } finally {
        Remove-Item Env:OPENVISIO_GUI_TESTS -ErrorAction SilentlyContinue
    }
    Invoke-UnitPattern -Pattern 'test_node_label_fidelity_v4319.py'
    python -m pip install --disable-pip-version-check -r '02-Compilation/requirements-build.txt'
    if ($LASTEXITCODE -ne 0) { throw 'Pinned PyInstaller installation failed' }
    $portable = Join-Path $root 'dist/OpenVisio-V43.27-Source-Candidate-Windows-x64-Portable.exe'
    $installer = Join-Path $root 'dist/installer/OpenVisio-V43.27-Source-Candidate-Setup-x64.exe'
    foreach ($file in @($portable, $installer)) {
        if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file -Force }
    }
    python -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name OpenVisio-V43.27-Source-Candidate-Windows-x64-Portable `
        --paths python python/run_openvisio.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
    if (!(Test-Path -LiteralPath $portable)) { throw 'Portable EXE absent' }
    & (Join-Path $root '04-Tests/Smoke-Portable-V42.71.ps1') -Executable $portable
    if ($LASTEXITCODE -ne 0) { throw 'Frozen functional smoke failed' }
    $iscc = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6/ISCC.exe'
    if (!(Test-Path -LiteralPath $iscc)) { throw 'Inno Setup 6 absent' }
    & $iscc '02-Compilation/installer/OpenVisio-V43.27-Candidate.iss'
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed' }
    if (!(Test-Path -LiteralPath $installer)) { throw 'Installer EXE absent' }
    & (Join-Path $root '04-Tests/Smoke-Installer-V42.71.ps1') -Installer $installer
    if ($LASTEXITCODE -ne 0) { throw 'Installer functional smoke failed' }
    $manifest = Join-Path $root 'dist/OpenVisio-V43.27-Source-Candidate-Windows-SHA256.txt'
    @($portable, $installer) | ForEach-Object {
        $hash = Get-FileHash -LiteralPath $_ -Algorithm SHA256
        "$($hash.Hash.ToLowerInvariant())  $([IO.Path]::GetFileName($_))"
    } | Set-Content -LiteralPath $manifest -Encoding ascii
    $sourceCommit = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $sourceCommit -notmatch '^[0-9a-f]{40}$') { throw 'Unable to identify exact source commit' }
    $qualificationPath = Join-Path $root 'dist/V43.27-Windows-Qualification.json'
    $qualification = [ordered]@{
        version = 'V43.27'
        author = 'Abdelhalim Talbi'
        source_branch = 'develop/v43.27-formula-driven-vsdx-geometry-20261026'
        source_commit = $sourceCommit
        generated_utc = [DateTime]::UtcNow.ToString('o')
        runner = 'GitHub Actions windows-2022'
        python = (& python --version 2>&1 | Out-String).Trim()
        unit_suite = [ordered]@{
            status = 'PASS'
            executed_tests = $unitCount
            skipped_tests = $skipCount
            duration_seconds = $unitDuration
            log = '06-Evidence/Windows-Test-Logs/full-python-suite.log'
        }
        targeted_regressions = @(
            'test_release_archive_guard_v4320.py',
            'test_vsdx_zip_path_canonical_v4321.py',
            'test_vsdx_embedded_part_canonical_v4322.py',
            'test_vsdx_static_route_preservation_v4322.py',
            'test_vsdx_route_endpoint_attachment_v4324.py',
            'test_vsdx_route_spatial_prefilter_v4325.py',
            'test_vsdx_formula_geometry_fidelity_v4327.py',
            'test_vsdx_route_segment_prefilter_v4325.py',
            'test_low_zoom_label_lod_v4320.py',
            'test_node_label_fidelity_v4319.py'
        )
        checkout_and_parity = 'PASS'
        archive_source_guard = 'PASS'
        portable_build = 'PASS'
        portable_smoke = 'PASS'
        installer_build = 'PASS'
        installer_smoke = 'PASS'
        microsoft_visio_desktop = 'NOT_TESTED'
        manual_windows_acceptance = 'NOT_PERFORMED'
        application_screenshots = 'NOT_AVAILABLE'
        internal_application_version = '42.50.0'
        notes = @(
            'Candidate build and automated smoke only; no manual Windows GUI acceptance.',
            'No real Microsoft Visio Desktop import/export round-trip was performed.',
            'DOCX is structurally checked; PDF pages are rendered and checked for text bounds.'
        )
    }
    $qualification | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $qualificationPath -Encoding utf8

    $docOut = Join-Path $root 'dist/release-docs'
    python 02-Compilation/generate_release_docs_v4327.py --root $root --out-dir $docOut --commit $sourceCommit --qualification-json $qualificationPath
    if ($LASTEXITCODE -ne 0) { throw 'Release Word/PDF generation or PDF render QA failed' }

    $cumulative = Join-Path $root 'dist/OpenVisio-V43.27-Cumulative-Windows-x64.zip'
    python 02-Compilation/package_cumulative_release_v4327.py --root $root --portable $portable --installer $installer --qualification-json $qualificationPath --docx (Join-Path $docOut 'OpenVisio-V43.27-Architecture-and-Qualification.docx') --pdf (Join-Path $docOut 'OpenVisio-V43.27-Architecture-and-Qualification.pdf') --document-qa-json (Join-Path $docOut 'document-qa.json') --document-qa-renders (Join-Path $docOut 'pdf-page-renders') --output $cumulative
    if ($LASTEXITCODE -ne 0) { throw 'Cumulative ZIP failed independent integrity validation' }
    Write-Host 'PASS: Windows source candidate built; portable/installer smoke, docs QA and cumulative ZIP integrity passed'
} finally {
    Pop-Location
}
