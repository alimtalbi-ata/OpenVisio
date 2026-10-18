param(
 [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
 [int]$StartupSeconds = 12,
 [int]$ProcessTimeoutSeconds = 180
)
$ErrorActionPreference = 'Stop'
# Installing the machine-wide Inno package requires an elevated shell.
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
 throw 'Installer E2E must run from an elevated PowerShell session (Run as administrator)'
}
$package = Get-Content -Raw (Join-Path $Root 'package.json') | ConvertFrom-Json
$version = $package.version -replace '\.0$', ''
$installer = Join-Path $Root "dist/installer/OpenVisio-Setup-v$version-x64.exe"
$installDir = Join-Path $env:TEMP "OpenVisio-Installer-Qualification-$PID"
$logDir = Join-Path $Root 'dist/qualification'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir 'installer-e2e.log'
$reportFile = Join-Path $logDir 'installer-e2e-result.json'
if (!(Test-Path -LiteralPath $installer)) { throw "Installer missing: $installer" }
if ((Get-Item -LiteralPath $installer).Length -lt 1MB) { throw 'Installer too small' }
$report = [ordered]@{ version=$version; install='NOT_RUN'; assets='NOT_RUN'; startup='NOT_RUN'; uninstall='NOT_RUN'; cleanup='NOT_RUN'; status='NOT_RUN'; error=$null }
function Invoke-InstallerProcess([string]$File, [string[]]$Arguments, [string]$Phase) {
 $p = Start-Process -FilePath $File -ArgumentList $Arguments -PassThru
 try {
  if (!$p.WaitForExit($ProcessTimeoutSeconds * 1000)) {
   Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
   throw "$Phase timed out after $ProcessTimeoutSeconds seconds"
  }
  if ($p.ExitCode -ne 0) { throw "$Phase exit code: $($p.ExitCode)" }
 } finally { $p.Dispose() }
}
try {
 Write-Host "Installing into $installDir"
 Invoke-InstallerProcess $installer @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=$installDir","/LOG=$logFile") 'Install'
 $report.install = 'PASS'
 foreach ($relative in @('OpenVisio.exe','wwwroot/index.html','wwwroot/src/main.js','wwwroot/styles/app.css')) {
  $path = Join-Path $installDir $relative
  if (!(Test-Path -LiteralPath $path)) { throw "Missing installed asset: $relative" }
 }
 $report.assets = 'PASS'
 $exe = Join-Path $installDir 'OpenVisio.exe'
 $app = Start-Process -FilePath $exe -PassThru
 try {
  Start-Sleep -Seconds $StartupSeconds
  $app.Refresh()
  if ($app.HasExited) { throw "Application exited during startup: $($app.ExitCode)" }
  $report.startup = 'PASS'
 } finally {
  if (!$app.HasExited) { Stop-Process -Id $app.Id -Force -ErrorAction SilentlyContinue }
  $app.Dispose()
 }
} catch { $report.error=$_.Exception.Message; throw } finally {
 try {
  $uninstall = Join-Path $installDir 'unins000.exe'
  if (!(Test-Path -LiteralPath $uninstall)) { throw 'Uninstaller missing' }
  Invoke-InstallerProcess $uninstall @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') 'Uninstall'
  $report.uninstall = 'PASS'
  if (Test-Path -LiteralPath (Join-Path $installDir 'OpenVisio.exe')) { throw 'Executable remains after uninstall' }
  $report.cleanup = 'PASS'
 } finally {
  $report.status = if (@('install','assets','startup','uninstall','cleanup') | Where-Object { $report[$_] -ne 'PASS' }) { 'FAIL' } else { 'PASS' }
  $report | ConvertTo-Json | Set-Content -Encoding utf8 $reportFile
  Write-Host ($report | ConvertTo-Json)
 }
}
