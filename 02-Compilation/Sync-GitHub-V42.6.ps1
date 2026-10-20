# Requires Git for Windows, GitHub CLI (gh) and authenticated gh auth login.
# Preserves main and refuses dirty checkouts or pre-existing untracked target files.
param([string]$Repo='alimtalbi-ata/OpenVisio',[string]$Branch='develop/v42.6-windows-qualification')
$ErrorActionPreference='Stop'
$packageRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (!(Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git not installed' }
if (!(Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI not installed' }
gh auth status | Out-Host
if ($LASTEXITCODE -ne 0) { throw 'Run gh auth login first' }
$temp = Join-Path ([IO.Path]::GetTempPath()) ('openvisio-v426-'+[guid]::NewGuid().ToString('N'))
try {
  git clone "https://github.com/$Repo.git" $temp
  if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
  Push-Location $temp
  try {
    git fetch origin $Branch
    if ($LASTEXITCODE -ne 0) { throw 'Branch missing on origin' }
    git switch --track "origin/$Branch"
    if ($LASTEXITCODE -ne 0) { throw 'Cannot switch branch' }
    $paths = @('03-Sources','02-Compilation','04-Tests','05-Documentation','07-Manifestes')
    foreach ($p in $paths) {
      $source = Join-Path $packageRoot $p
      if (!(Test-Path $source)) { throw "Missing package directory $p" }
      Get-ChildItem -LiteralPath $source -Recurse -File | ForEach-Object {
        $rel = [IO.Path]::GetRelativePath($packageRoot,$_.FullName)
        $target = Join-Path $temp $rel
        if (!(Test-Path $target)) { New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null }
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
      }
    }
    # Exclude old binary executables and local build outputs from source commit.
    git add -- 03-Sources 02-Compilation 04-Tests 05-Documentation 07-Manifestes
    git diff --cached --check
    if ($LASTEXITCODE -ne 0) { throw 'Whitespace/patch validation failed' }
    git diff --cached --stat | Out-Host
    Write-Host 'Review the staged changes before publishing. Main remains untouched.'
    $changes = git diff --cached --name-only
    if (!$changes) { Write-Host 'No source changes to publish'; return }
    git commit -m 'build: synchronize cumulative V42.6 sources and Windows packaging'
    if ($LASTEXITCODE -ne 0) { throw 'Commit failed' }
    git push origin "HEAD:$Branch"
    if ($LASTEXITCODE -ne 0) { throw 'Push failed; inspect branch divergence' }
    Write-Host "Published $Branch; inspect Actions before release qualification"
  } finally { Pop-Location }
} finally { if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force } }
