# Author: Abdelhalim Talbi. Portable mono-EXE; WebView2 runtime remains an OS prerequisite.
param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path)
$ErrorActionPreference = 'Stop'
$dotnet = Join-Path $Root 'dist\build-tools\dotnet\dotnet.exe'
if (!(Test-Path $dotnet)) { throw 'SDK .NET absent. Executer Build-OpenVisio-Windows.cmd.' }
$assets = Join-Path $Root 'windows\native\openvisio-assets.zip'
if (Test-Path $assets) { Remove-Item $assets -Force }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$rootPath = (Resolve-Path $Root).Path
$fs = [System.IO.File]::Open($assets, [System.IO.FileMode]::Create)
try {
 $archive = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Create, $true)
 try {
  $paths = @((Join-Path $Root 'index.html')) + @(Get-ChildItem (Join-Path $Root 'src'),(Join-Path $Root 'styles'),(Join-Path $Root 'assets') -File -Recurse | Select-Object -ExpandProperty FullName)
  foreach ($path in $paths) {
   $relative = $path.Substring($rootPath.Length + 1).Replace('\','/')
   [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $path, $relative, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
  }
 } finally { $archive.Dispose() }
} finally { $fs.Dispose() }
$publish = Join-Path $Root 'dist\portable\publish'
if (Test-Path $publish) { Remove-Item $publish -Recurse -Force }
& $dotnet publish (Join-Path $Root 'windows\native\OpenVisio.csproj') -c Release -r win-x64 --self-contained true '-p:PublishSingleFile=true' '-p:IncludeNativeLibrariesForSelfExtract=true' '-p:OpenVisioEmbedAssets=true' -o $publish
if ($LASTEXITCODE -ne 0) { throw 'Publication mono-EXE echouee' }
$exe = Join-Path $publish 'OpenVisio.exe'
if (!(Test-Path $exe)) { throw 'OpenVisio.exe absent' }
$files = @(Get-ChildItem $publish -File)
$extra = @($files | Where-Object { $_.Name -ne 'OpenVisio.exe' -and $_.Extension -notin @('.pdb') })
if ($extra.Count -gt 0) { throw ('Publication non mono-EXE: ' + ($extra.Name -join ', ')) }
# Read the assembly version from the project to prevent stale portable filenames.
$project = Join-Path $Root 'windows\native\OpenVisio.csproj'
[xml]$projectXml = Get-Content -LiteralPath $project -Raw
$version = [string]$projectXml.Project.PropertyGroup.Version
if ($version -notmatch '^(\d+)\.(\d+)\.\d+$') { throw 'Version projet invalide' }
$release = "$($Matches[1]).$($Matches[2])"
$target = Join-Path $Root ("dist\portable\OpenVisio-v{0}-Windows-x64-Portable.exe" -f $release)
if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
Copy-Item $exe $target -Force
if ((Get-Item -LiteralPath $target).Length -lt 1000000) { throw "Portable anormalement petit" }
Get-FileHash -LiteralPath $target -Algorithm SHA256 | Format-List
Write-Host "Portable mono-EXE cree: $target"
