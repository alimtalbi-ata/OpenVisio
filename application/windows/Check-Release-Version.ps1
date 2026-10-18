$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$package = Get-Content (Join-Path $root 'package.json') -Raw | ConvertFrom-Json
[xml]$project = Get-Content (Join-Path $root 'windows/native/OpenVisio.csproj') -Raw
$version = [string]$package.version
if ($version -ne [string]$project.Project.PropertyGroup.Version) { throw "Version mismatch package=$version csproj=$($project.Project.PropertyGroup.Version)" }
$iss = Get-Content (Join-Path $root 'windows/installer/OpenVisio.iss') -Raw
if ($iss -notmatch ('(?m)^#define AppVersion "' + [regex]::Escape($version) + '"')) { throw 'Inno Setup version mismatch' }
$parts = $version.Split('.')
$filename = "OpenVisio-Setup-v$($parts[0]).$($parts[1])-x64"
if ($iss -notmatch [regex]::Escape('OutputBaseFilename=' + $filename)) { throw 'Inno Setup output name mismatch' }
Write-Host "Release version consistency PASS: $version"
