# Run against a REAL frozen Windows executable, from a source-free directory.
# Author: Abdelhalim Talbi. Synthetic document fidelity only.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Executable)
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $Executable).Path
$isolated = Join-Path $env:TEMP ('openvisio-v4271-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $isolated | Out-Null
$exe = Join-Path $isolated 'OpenVisio.exe'
Copy-Item -LiteralPath $source -Destination $exe -Force
$prior = [Environment]::GetEnvironmentVariable('OPENVISIO_SMOKE_REPORT','Process')
$proc = $null
try {
    $report = Join-Path $isolated 'frozen-smoke.json'
    [Environment]::SetEnvironmentVariable('OPENVISIO_SMOKE_REPORT', $report, 'Process')
    $proc = Start-Process -FilePath $exe -WorkingDirectory $isolated -PassThru
    if (!$proc.WaitForExit(60000)) { throw 'Frozen smoke timed out' }
    if ($proc.ExitCode -ne 0 -or !(Test-Path -LiteralPath $report)) { throw 'Frozen smoke failed' }
    $result = Get-Content -LiteralPath $report -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($result.status -ne 'PASS' -or $result.version -ne '42.50.0' -or
        $result.scope -ne 'packaged-executable-io-synthetic' -or
        $result.microsoft_visio_qualified -ne $false) { throw 'Invalid frozen smoke evidence' }
    foreach ($name in @('ovjson-save-reopen','editor-bounded-open-revision','svg-parse',
                       'vsdx-public-geometry','vsdx-save-reopen','vsdx-no-clobber')) {
        if ($result.checks -notcontains $name) { throw "Missing check: $name" }
    }
    [Environment]::SetEnvironmentVariable('OPENVISIO_SMOKE_REPORT', $null, 'Process')
    $proc = Start-Process -FilePath $exe -WorkingDirectory $isolated -PassThru
    Start-Sleep -Seconds 6
    $proc.Refresh()
    if ($proc.HasExited) { throw "Tk GUI exited early: $($proc.ExitCode)" }
    Write-Host 'PASS: frozen executable IO and Tk GUI startup from source-free directory'
} finally {
    [Environment]::SetEnvironmentVariable('OPENVISIO_SMOKE_REPORT', $prior, 'Process')
    if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
    Remove-Item -LiteralPath $isolated -Recurse -Force -ErrorAction SilentlyContinue
}
