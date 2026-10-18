param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path)
$ErrorActionPreference = 'Stop'
$required = @('package.json','index.html','src/main.js','styles/app.css','windows/native/OpenVisio.csproj','windows/native/Program.cs','windows/installer/OpenVisio.iss')
foreach ($relative in $required) {
  $file = Join-Path $Root $relative
  if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Source missing: $relative" }
  if ((Get-Item -LiteralPath $file).Length -eq 0) { throw "Source empty: $relative" }
}
$package = Get-Content -Raw (Join-Path $Root 'package.json') | ConvertFrom-Json
$installer = Get-Content -Raw (Join-Path $Root 'windows/installer/OpenVisio.iss')
$version = [string]$package.version
if ($version -notmatch '^\d+\.\d+\.0$') { throw 'Invalid release version format' }
$shortVersion = $version -replace '\.0$', ''
$escapedShortVersion = [regex]::Escape($shortVersion)
$escapedVersion = [regex]::Escape($version)
if ($installer -notmatch "OutputBaseFilename=OpenVisio-Setup-v$escapedShortVersion-x64") {
  throw 'Version mismatch between package and Windows installer'
}
Write-Host 'PASS: source files and release version are consistent'

# Verify .NET project identity, embedded resources and Windows packaging references.
$project = Get-Content -Raw (Join-Path $Root 'windows/native/OpenVisio.csproj')
$source = Get-Content -Raw (Join-Path $Root 'windows/native/Program.cs')
$builder = Get-Content -Raw (Join-Path $Root 'Build-OpenVisio-Windows.cmd')
if ($project -notmatch "<Version>$escapedVersion</Version>") { throw 'Assembly version mismatch' }
if ($project -notmatch 'CopyToPublishDirectory') { throw 'Editor assets not included in publish' }
if ($source -notmatch 'WebView2') { throw 'Desktop browser component missing' }
if ($builder -notmatch "OpenVisio-Setup-v$escapedShortVersion-x64\.exe") { throw 'Build output mismatch' }
Write-Host 'PASS: native shell and installer configuration'

if ($installer -notmatch "#define AppVersion `"$escapedVersion`"") { throw 'Inno AppVersion mismatch' }

# Parse all PowerShell entrypoints before fetching build dependencies.
$scriptFiles = Get-ChildItem (Join-Path $Root 'windows') -Filter '*.ps1' -File
$scriptFiles += Get-Item (Join-Path $Root 'windows/openvisio.ps1') -ErrorAction SilentlyContinue | Where-Object { $_ -and $_ -notin $scriptFiles }
foreach ($scriptFile in ($scriptFiles | Sort-Object FullName -Unique)) {
  $tokens = $null
  $parseErrors = $null
  [void][System.Management.Automation.Language.Parser]::ParseFile($scriptFile.FullName, [ref]$tokens, [ref]$parseErrors)
  if ($parseErrors.Count -gt 0) { throw "PowerShell syntax invalid: $($scriptFile.Name): $($parseErrors[0].Message)" }
}
Write-Host 'PASS: Windows PowerShell scripts parse successfully'
# Ensure every local JS/CSS module linked from index.html exists before packaging.
$html = Get-Content -Raw (Join-Path $Root 'index.html')
$assetRefs = [regex]::Matches($html, '(?:src|href)=["'']((?:src|styles|assets)/[^"''?#]+)["'']')
foreach ($match in $assetRefs) {
  $relative = $match.Groups[1].Value
  if (-not (Test-Path -LiteralPath (Join-Path $Root $relative) -PathType Leaf)) { throw "HTML asset missing: $relative" }
}
Write-Host "PASS: $($assetRefs.Count) local HTML assets found"
