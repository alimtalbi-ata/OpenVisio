# OpenVisio v24.8 — recette Chromium Windows. Auteur : Abdelhalim Talbi.
param([string]$Python="py", [string]$Baseline="", [string]$Chromium="", [string]$Output="qualification-windows", [string]$VisualBaseline="", [double]$VisualThreshold=0.02)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
New-Item -ItemType Directory -Force -Path $Output | Out-Null
& $Python -c "import playwright" 2>$null
if ($LASTEXITCODE -ne 0) { throw "Playwright Python absent. Installer avec: py -m pip install playwright; py -m playwright install chromium" }
$argsList = @("tests/browser-san-performance.py", "--report", "$Output/browser-report.json", "--screenshot", "$Output/openvisio-ui-real.png", "--comparison-report", "$Output/comparison.json")
if ($Baseline) { $argsList += @("--baseline", $Baseline) }
if ($Chromium) { $argsList += @("--chromium", $Chromium) }
if ($VisualBaseline) { $argsList += @("--visual-baseline", $VisualBaseline, "--visual-threshold", "$VisualThreshold") }
& $Python @argsList
if ($LASTEXITCODE -ne 0) { throw "Recette graphique échouée : consulter $Output/browser-report.json" }
Write-Host "Recette PASS. Capture reelle : $Output/openvisio-ui-real.png"
