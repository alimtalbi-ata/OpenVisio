# Windows release qualification with evidence. Author: Abdelhalim Talbi.
param(
 [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
 [switch]$SkipInstaller,
 [switch]$SkipNativeSmoke,
 [switch]$SkipPortableSmoke,
 [switch]$RunGraphicSmoke,
 [switch]$RunFunctionalSmoke,
 [string]$Python = "py"
)
$ErrorActionPreference = 'Stop'
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$dist = Join-Path $rootPath 'dist/qualification'
New-Item -ItemType Directory -Force -Path $dist | Out-Null
$version = [string](Get-Content -Raw (Join-Path $rootPath 'package.json') | ConvertFrom-Json).version
$report = [ordered]@{
 schema='openvisio.windows.qualification.v1'; version=$version
 timestamp_utc=(Get-Date).ToUniversalTime().ToString('o')
 machine=$env:COMPUTERNAME; checks=@(); status='INCOMPLETE'
}
function Invoke-Check([string]$Name,[scriptblock]$Action) {
 $record = [ordered]@{ name=$Name; status='NOT_RUN'; error=$null }
 try { & $Action; $record.status='PASS' }
 catch { $record.status='FAIL'; $record.error=$_.Exception.Message; $record['detail']=$_.ScriptStackTrace }
 $report.checks += $record
 Write-Host "[$($record.status)] $Name $($record.error)"
}
try {
 Invoke-Check 'preflight' { & (Join-Path $rootPath 'windows/Preflight-Windows.ps1') -Root $rootPath; if (-not $?) { throw 'Preflight returned failure' };  }
 $exe = Join-Path $rootPath 'dist/windows-x64/OpenVisio.exe'
 Invoke-Check 'published_assets' {
  foreach ($relative in @('OpenVisio.exe','wwwroot/index.html','wwwroot/src/main.js','wwwroot/styles/app.css')) {
   if (-not (Test-Path -LiteralPath (Join-Path $rootPath "dist/windows-x64/$relative") -PathType Leaf)) { throw "Missing published file: $relative" }
  }
 }
 if (-not $SkipNativeSmoke) {
  Invoke-Check 'native_http_smoke' { & (Join-Path $rootPath 'windows/Validate-OpenVisio-Windows.ps1') -Executable $exe; if (-not $?) { throw 'Native smoke returned failure' }; if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Native smoke exit code $LASTEXITCODE" } }
 } else { $report.checks += [ordered]@{name='native_http_smoke';status='SKIPPED';error=$null} }
 if (-not $SkipPortableSmoke) {
  Invoke-Check 'portable_artifact_smoke' {
   & (Join-Path $rootPath 'windows/Test-Portable-Artifact.ps1') -Root $rootPath
   if (-not $?) { throw 'Portable validation failed' }
  }
 } else { $report.checks += [ordered]@{name='portable_artifact_smoke';status='SKIPPED';error=$null} }
 if (-not $SkipInstaller) {
  Invoke-Check 'installer_e2e' { & (Join-Path $rootPath 'windows/Test-Installer-E2E.ps1') -Root $rootPath; if (-not $?) { throw 'Installer E2E returned failure' }; if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Installer E2E exit code $LASTEXITCODE" } }
 } else { $report.checks += [ordered]@{name='installer_e2e';status='SKIPPED';error=$null} }
 if ($RunGraphicSmoke) {
  Invoke-Check 'graphic_browser_smoke' {
   & (Join-Path $rootPath 'windows/Run-Graphic-Qualification.ps1') -Python $Python -Output (Join-Path $dist 'browser')
   if (-not $?) { throw 'Graphic smoke returned failure' }
   if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Graphic smoke exit code $LASTEXITCODE" }
   foreach ($asset in @('browser-report.json','openvisio-ui-real.png')) {
    if (-not (Test-Path -LiteralPath (Join-Path $dist "browser/$asset") -PathType Leaf)) { throw "Graphic evidence missing: $asset" }
   }
  }
 } else { $report.checks += [ordered]@{name='graphic_browser_smoke';status='SKIPPED';error=$null} }
 if ($RunFunctionalSmoke) {
  Invoke-Check 'functional_browser_smoke' {
   $functionalDir = Join-Path $dist 'functional'
   New-Item -ItemType Directory -Force -Path $functionalDir | Out-Null
   & $Python (Join-Path $rootPath 'tests/browser-functional-v361.py') --output $functionalDir
   if ($LASTEXITCODE -ne 0) { throw "Functional smoke exit code $LASTEXITCODE" }
   $functionalReport = Join-Path $functionalDir 'functional-report.json'
   if (-not (Test-Path -LiteralPath $functionalReport -PathType Leaf)) { throw 'Functional report missing' }
   $result = Get-Content -Raw -LiteralPath $functionalReport | ConvertFrom-Json
   if ($result.status -ne 'PASS') { throw "Functional smoke did not pass: $($result.status)" }
  }
 } else { $report.checks += [ordered]@{name='functional_browser_smoke';status='SKIPPED';error=$null} }
 $statuses = @($report.checks | ForEach-Object { $_.status })
 if ($statuses -contains 'FAIL') { $report.status='FAIL' }
 elseif ($statuses -contains 'SKIPPED') { $report.status='PARTIAL' }
 else { $report.status='PASS' }
} finally {
 $path = Join-Path $dist 'qualification-summary.json'
 $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding UTF8
 Write-Host "Qualification report: $path ($($report.status))"
}
if ($report.status -eq 'FAIL') { exit 1 }
if ($report.status -eq 'PARTIAL') { exit 2 }
exit 0
