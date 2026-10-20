# OpenVisio candidate synchronization: GitHub branch + optional draft PR.
# Author: Abdelhalim Talbi. Requires Git and authenticated gh CLI.
param(
  [string]$Repository = 'alimtalbi-ata/OpenVisio',
  [string]$BaseBranch = 'develop/v42.6-windows-qualification',
  [string]$TargetBranch = 'develop/v42.6-vsdx-preview',
  [switch]$DryRun,
  [switch]$SkipPullRequest
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
foreach ($tool in @('git','gh')) {
  if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "Missing prerequisite: $tool" }
}
gh auth status | Out-Host
if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI authentication required' }
$temp = Join-Path ([IO.Path]::GetTempPath()) ('openvisio-sync-' + [guid]::NewGuid().ToString('N'))
try {
  & git clone --quiet "https://github.com/$Repository.git" $temp
  if ($LASTEXITCODE -ne 0) { throw 'Git clone failed' }
  Push-Location $temp
  try {
    & git fetch origin $BaseBranch
    if ($LASTEXITCODE -ne 0) { throw 'Cannot fetch baseline branch' }
    & git switch -c $TargetBranch "origin/$BaseBranch"
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create candidate branch' }
    foreach ($folder in @('02-Compilation','03-Sources','04-Tests','05-Documentation','07-Manifestes')) {
      $source = Join-Path $root $folder
      if (!(Test-Path $source)) { throw "Missing source folder $folder" }
      Get-ChildItem -LiteralPath $source -Recurse -File | ForEach-Object {
        $rel = [IO.Path]::GetRelativePath($root, $_.FullName)
        if ($rel -match '(^|[\\/])(__pycache__|\.venv|dist|build)([\\/]|$)' -or $rel -match '\.(pyc|pyo)$') { return }
        $target = Join-Path $temp $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
      }
    }
    & git add -- 02-Compilation 03-Sources 04-Tests 05-Documentation 07-Manifestes
    & git diff --cached --check
    if ($LASTEXITCODE -ne 0) { throw 'Patch whitespace check failed' }
    & git diff --cached --stat | Out-Host
    $changed = @(& git diff --cached --name-only)
    if ($changed.Count -eq 0) { Write-Host 'No changes'; return }
    if ($DryRun) { Write-Host 'Dry run: no commit or push performed'; return }
    & git commit -m 'feat: lossless layers and experimental VSDX interoperability with tests'
    if ($LASTEXITCODE -ne 0) { throw 'Commit failed' }
    & git push --set-upstream origin "HEAD:$TargetBranch"
    if ($LASTEXITCODE -ne 0) { throw 'Push failed; remote branch not overwritten' }
    if (-not $SkipPullRequest) {
      & gh pr create --repo $Repository --base main --head $TargetBranch --draft `
        --title 'WIP: OpenVisio V42.6 VSDX interoperability and layers' `
        --body 'Experimental VSDX, 134 Python unit tests local. Do not merge: full Windows CI and Microsoft Visio fidelity qualification pending.'
      if ($LASTEXITCODE -ne 0) { throw 'Push succeeded but draft PR creation failed' }
    }
  } finally { Pop-Location }
} finally {
  if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
