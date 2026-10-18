param([Parameter(Mandatory=$true)][string]$Executable)
$ErrorActionPreference = 'Stop'
if (!(Test-Path -LiteralPath $Executable)) { throw 'OpenVisio.exe missing' }
$root = Split-Path -Parent $Executable
foreach ($asset in @('wwwroot/index.html','wwwroot/src/main.js','wwwroot/styles/app.css')) {
 if (!(Test-Path -LiteralPath (Join-Path $root $asset))) { throw "Missing asset: $asset" }
}
$out = Join-Path $env:TEMP ("openvisio-smoke-" + [guid]::NewGuid().ToString('N') + '.log')
$err = $out + '.err'
$proc = Start-Process -FilePath $Executable -ArgumentList '--no-browser' -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
try {
 $url = $null
 for ($i=0; $i -lt 50; $i++) {
  Start-Sleep -Milliseconds 200
  if (Test-Path $out) {
   $content = Get-Content $out -Raw
   if ($content -match '(http://127\.0\.0\.1:\d+/)') { $url = $Matches[1]; break }
  }
  if ($proc.HasExited) { break }
 }
 if (!$url) { throw 'Server did not start or report loopback URL' }
 foreach ($asset in @('','src/main.js','styles/app.css')) {
  $response = Invoke-WebRequest -Uri ($url+$asset) -UseBasicParsing -TimeoutSec 5
  if ($response.StatusCode -ne 200) { throw "HTTP smoke failed: $asset" }
 }
 # Security and protocol smoke checks on the native Windows host.
 $head = Invoke-WebRequest -Uri ($url+'index.html') -Method Head -UseBasicParsing -TimeoutSec 5
 if ($head.StatusCode -ne 200) { throw 'HEAD /index.html failed' }
 if ($head.Headers['X-Content-Type-Options'] -ne 'nosniff') { throw 'nosniff header missing' }
 if ($head.Headers['X-Frame-Options'] -ne 'DENY') { throw 'frame protection missing' }
 try {
  Invoke-WebRequest -Uri ($url+'index.html') -Method Post -UseBasicParsing -TimeoutSec 5 | Out-Null
  throw 'POST was incorrectly accepted'
 } catch [System.Net.WebException] {
  if ([int]$_.Exception.Response.StatusCode -ne 405) { throw 'POST did not return 405' }
 }
 try {
  Invoke-WebRequest -Uri ($url+'missing-openvisio-asset.js') -UseBasicParsing -TimeoutSec 5 | Out-Null
  throw 'Missing asset was incorrectly accepted'
 } catch [System.Net.WebException] {
  if ([int]$_.Exception.Response.StatusCode -ne 404) { throw 'Missing asset did not return 404' }
 }
 Write-Host "PASS: Windows EXE loopback smoke test $url"
} finally {
 if (!$proc.HasExited) { Stop-Process -Id $proc.Id -Force }
 Remove-Item $out,$err -Force -ErrorAction SilentlyContinue
}
