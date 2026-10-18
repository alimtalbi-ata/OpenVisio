# Windows PowerShell 5.1+; isolated synthetic scenarios; never modify production binaries.
param(
  [string]$Script = (Join-Path $PSScriptRoot 'Inspect-Binary-Recovery.ps1'),
  [string]$ReportPath = (Join-Path $PSScriptRoot 'recovery-scenario-report.json')
)
$ErrorActionPreference = 'Stop'
$root = Join-Path ([IO.Path]::GetTempPath()) ('openvisio-recovery-test-' + [guid]::NewGuid().ToString('N'))
$results = [System.Collections.Generic.List[object]]::new()
$failed = $false
function Add-Scenario([string]$Name, [bool]$Passed, [string]$Detail) {
  $script:results.Add([pscustomobject]@{ name=$Name; pass=$Passed; detail=$Detail })
  if (-not $Passed) { $script:failed = $true }
}
function Assert-Rejected([string]$Name, [scriptblock]$Action) {
  $rejected = $false
  try { & $Action | Out-Null } catch { $rejected = $true }
  Add-Scenario $Name $rejected 'Operation must be rejected'
}
try {
  New-Item -ItemType Directory -Path $root -Force | Out-Null
  try {
    & $Script -Root $root | Out-Null
    $assessment = Get-Content (Join-Path $root 'binary-recovery-assessment.json') -Raw | ConvertFrom-Json
    Add-Scenario 'empty-inspection' (-not $assessment.binaryValid -and -not $assessment.previousValid -and $assessment.status -eq 'PASS') 'Empty directory must be assessed safely'
  } catch { Add-Scenario 'empty-inspection' $false $_.Exception.Message }
  Assert-Rejected 'confirmation-required' { & $Script -Root $root -RestorePrevious }
  New-Item -ItemType Directory -Path (Join-Path $root 'binary.pending') -Force | Out-Null
  Assert-Rejected 'pending-blocks-restore' { & $Script -Root $root -RestorePrevious -ConfirmRecovery }
  Remove-Item -LiteralPath (Join-Path $root 'binary.pending') -Recurse -Force
  # Synthetic MZ fixtures test the recovery state machine, NOT executable Windows applications.
  $backup = Join-Path $root 'binary.previous'
  New-Item -ItemType Directory -Path $backup -Force | Out-Null
  $artifacts = @()
  foreach ($kind in @('installer','portable')) {
    $name = 'fixture-' + $kind + '.exe'
    $path = Join-Path $backup $name
    $bytes = New-Object byte[] 1000000
    $bytes[0] = 77; $bytes[1] = 90
    [IO.File]::WriteAllBytes($path, $bytes)
    $artifacts += @{kind=$kind;file=$name;bytes=1000000;sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash}
  }
  @{status='PASS';artifacts=$artifacts} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $backup 'manifest.json') -Encoding UTF8
  & $Script -Root $root -RestorePrevious -ConfirmRecovery | Out-Null
  $after = Get-Content -LiteralPath (Join-Path $root 'binary-recovery-assessment.json') -Raw | ConvertFrom-Json
  Add-Scenario 'valid-checkpoint-restored' ($after.status -eq 'PASS' -and $after.action -eq 'RESTORED_PREVIOUS' -and $after.binaryValid -and !(Test-Path -LiteralPath $backup)) 'Synthetic checkpoint moved and revalidated'
  Assert-Rejected 'valid-binary-blocks-restore' { & $Script -Root $root -RestorePrevious -ConfirmRecovery }

} catch {
  Add-Scenario 'runner-exception' $false $_.Exception.Message
} finally {
  Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
  $report = [pscustomobject]@{ version='41.66'; status=$(if ($failed) {'FAIL'} else {'PASS'}); scenarios=@($results); generatedAt=(Get-Date).ToUniversalTime().ToString('o') }
  $reportDir = Split-Path -Parent $ReportPath
  if ($reportDir -and -not (Test-Path -LiteralPath $reportDir)) { New-Item -ItemType Directory -Path $reportDir -Force | Out-Null }
  $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ReportPath -Encoding UTF8
  Write-Host ('Recovery scenario tests: ' + $report.status + ' (' + @($results | Where-Object pass).Count + '/' + $results.Count + ')')
}
if ($failed) { exit 1 }
