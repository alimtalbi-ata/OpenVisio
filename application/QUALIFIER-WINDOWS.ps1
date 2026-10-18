# OpenVisio v20.3 - Auteur : Abdelhalim Talbi
# Exécuter dans PowerShell depuis le répertoire du projet.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$log = Join-Path $PSScriptRoot 'qualification-windows-v20.3.log'
"OpenVisio Windows qualification - $(Get-Date -Format o)" | Set-Content -Encoding UTF8 $log
"Windows: $([System.Environment]::OSVersion.VersionString)" | Add-Content $log
"PowerShell: $($PSVersionTable.PSVersion)" | Add-Content $log
try {
  $node = Get-Command node -ErrorAction Stop
  "Node: $(& node --version)" | Add-Content $log
  "NPM: $(& npm.cmd --version)" | Add-Content $log
  & npm.cmd test 2>&1 | Out-File -FilePath $log -Append -Encoding utf8
  if ($LASTEXITCODE -ne 0) { throw "Tests Node en échec (code $LASTEXITCODE)" }
  "RESULT=PASS_AUTOMATED_TESTS" | Add-Content $log
  Write-Host "Tests OK. Rapport : $log"
  Write-Host 'RECETTE MANUELLE A EFFECTUER : ouvrir index.html via serveur local, créer 2 équipements et une liaison SAN, éditer port et offset, annuler/rétablir, exporter/importer JSON, vérifier rendu SVG.'
  Write-Host 'CAPTURES : prendre des captures réelles, puis les placer dans snapshots/windows-v20.3/.'
} catch {
  "RESULT=FAIL: $_" | Add-Content $log
  Write-Error $_
  exit 1
}
