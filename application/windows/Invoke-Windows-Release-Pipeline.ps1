# Windows release pipeline with machine-readable evidence. Author: Abdelhalim Talbi.
param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
      [switch]$SkipBuild,
      [switch]$SkipInstallerE2E,
      [switch]$SkipStartup,
      [switch]$RunGraphicSmoke)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path
$dir = Join-Path $Root 'dist/qualification'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$version = (Get-Content -Raw (Join-Path $Root 'package.json') | ConvertFrom-Json).version
$report = [ordered]@{ schema='openvisio.windows.pipeline.v1'; version=$version; timestamp_utc=(Get-Date).ToUniversalTime().ToString('o'); status='NOT_RUN'; steps=@() }
function Step([string]$Name,[scriptblock]$Action,[bool]$Skip=$false) {
 $item=[ordered]@{name=$Name;status='NOT_RUN';error=$null}
 if($Skip){$item.status='SKIPPED'}
 else {
  try { & $Action; $item.status='PASS' }
  catch { $item.status='FAIL'; $item.error=$_.Exception.Message }
 }
 $report.steps += $item
 Write-Host "[$($item.status)] $Name $($item.error)"
 if($item.status -eq 'FAIL'){throw "$Name failed: $($item.error)"}
}
try {
 Step 'build_installer_and_portable' { & (Join-Path $Root 'Build-Windows-Installer.cmd'); if($LASTEXITCODE -ne 0){throw "Build exit $LASTEXITCODE"} } ([bool]$SkipBuild)
 Step 'release_metadata' { & node (Join-Path $Root 'windows/verify-release.mjs'); if($LASTEXITCODE -ne 0){throw "Release metadata exit $LASTEXITCODE"} }
 Step 'artifact_integrity' { & (Join-Path $Root 'windows/Test-Portable-Artifact.ps1') -Root $Root; if(-not $?){throw 'Portable integrity check failed'}; $manifest = Join-Path $Root 'binary/manifest.json'; if(!(Test-Path -LiteralPath $manifest)){throw 'Missing binary manifest'}; $m = Get-Content -Raw -LiteralPath $manifest | ConvertFrom-Json; if($m.status -ne 'PASS' -or @($m.artifacts).Count -ne 2){throw 'Binary manifest incomplete'}; foreach($artifact in $m.artifacts){$file=Join-Path (Join-Path $Root 'binary') $artifact.file; if(!(Test-Path -LiteralPath $file)){throw "Missing artifact: $file"}; if((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $artifact.sha256){throw "Artifact hash mismatch: $file"}} }
 Step 'native_startup' { & (Join-Path $Root 'windows/Test-Windows-Startup.ps1') -Root $Root -Mode Native -ReportDir $dir; if(-not $? -or (Get-Content -Raw (Join-Path $dir 'startup-native.json') | ConvertFrom-Json).startup -ne 'PASS'){throw 'Native startup failed'} } ([bool]$SkipStartup)
 Step 'portable_startup' { & (Join-Path $Root 'windows/Test-Windows-Startup.ps1') -Root $Root -Mode Portable -ReportDir $dir; if(-not $? -or (Get-Content -Raw (Join-Path $dir 'startup-portable.json') | ConvertFrom-Json).startup -ne 'PASS'){throw 'Portable startup failed'} } ([bool]$SkipStartup)
 Step 'installer_e2e' { & (Join-Path $Root 'windows/Test-Installer-E2E.ps1') -Root $Root; if(-not $?){throw 'Installer E2E failed'}; $e2e = Get-Content -Raw (Join-Path $dir 'installer-e2e-result.json') | ConvertFrom-Json; foreach($phase in @('install','assets','startup','uninstall','cleanup')){if($e2e.$phase -ne 'PASS'){throw "Installer phase $phase not PASS"}} } ([bool]$SkipInstallerE2E)
 Step 'browser_graphic' { & (Join-Path $Root 'windows/Run-Graphic-Qualification.ps1') -Output (Join-Path $dir 'browser'); if(-not $?){throw 'Browser graphic failed'} } (-not [bool]$RunGraphicSmoke)
 $report.status=if(@($report.steps | Where-Object {$_.status -eq 'SKIPPED'}).Count){'PARTIAL'}else{'PASS'}
} catch { $report.status='FAIL'; $report['error']=$_.Exception.Message }
finally { $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $dir ('pipeline-v' + $version + '.json')) -Encoding UTF8 }
if($report.status -eq 'FAIL'){exit 1}
if($report.status -eq 'PARTIAL'){exit 2}
exit 0
