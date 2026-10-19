@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "ROOT=%CD%"
set "TOOLS=%ROOT%\dist\build-tools"
set "DOTNET_ROOT=%TOOLS%\dotnet"
set "PATH=%DOTNET_ROOT%;%PATH%"
if not exist "%TOOLS%" mkdir "%TOOLS%"
if errorlevel 1 goto :error
if not exist "dist\installer" mkdir "dist\installer"
if errorlevel 1 goto :error
echo [0/5] Verification des sources et versions...
REM Portable artifacts are validated by Build-Portable-Windows.ps1; do not remove unrelated files.
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Check-Release-Version.ps1"
if errorlevel 1 goto :error
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Preflight-Windows.ps1"
if errorlevel 1 goto :error
REM Mandatory application regression tests before compiling release binaries.
where node.exe >nul 2>&1
if errorlevel 1 (echo Node.js requis pour la qualification de la release. & goto :error)
node --version
node --test tests
if errorlevel 1 (echo ECHEC: tests Node.js. & goto :error)
node windows/verify-release.mjs
if errorlevel 1 goto :error
echo [1/5] Preparation du SDK .NET 8 local...
if not exist "%DOTNET_ROOT%\dotnet.exe" (
 powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Invoke-WebRequest 'https://dot.net/v1/dotnet-install.ps1' -OutFile '%TOOLS%\dotnet-install.ps1'; & '%TOOLS%\dotnet-install.ps1' -Channel 8.0 -InstallDir '%DOTNET_ROOT%' -NoPath; if($LASTEXITCODE -ne 0){exit 1}"
 if errorlevel 1 goto :error
)
"%DOTNET_ROOT%\dotnet.exe" --list-sdks | findstr /r "^8\." >nul
if errorlevel 1 (echo SDK .NET 8 absent ou installation invalide. & goto :error)
echo [2/5] Preparation d'Inno Setup...
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not exist "%ISCC%" set "ISCC=%%I"
if not exist "%ISCC%" (
 where winget >nul 2>&1 || (echo Winget requis pour installer Inno Setup automatiquement. & goto :error)
 winget install --id JRSoftware.InnoSetup -e --accept-package-agreements --accept-source-agreements --silent
 if errorlevel 1 goto :error
)
REM winget does not update the parent cmd environment or necessarily use Program Files (x86).
if not exist "%ISCC%" if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not exist "!ISCC!" set "ISCC=%%I"
if not exist "%ISCC%" for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1" /v InstallLocation 2^>nul ^| findstr /i InstallLocation') do if exist "%%B\ISCC.exe" set "ISCC=%%B\ISCC.exe"
if not exist "%ISCC%" (echo Inno Setup introuvable apres installation. & goto :error)
echo [3/5] Recuperation du runtime WebView2 x64 pour l'installateur...
if not exist "dist\prerequisites" mkdir "dist\prerequisites"
if errorlevel 1 goto :error
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Invoke-WebRequest 'https://go.microsoft.com/fwlink/?linkid=2124701' -OutFile 'dist\prerequisites\MicrosoftEdgeWebView2RuntimeInstallerX64.exe'; if((Get-Item 'dist\prerequisites\MicrosoftEdgeWebView2RuntimeInstallerX64.exe').Length -lt 1000000){throw 'WebView2 download incomplete'}"
if errorlevel 1 goto :error
echo Verification de la signature du prerequis WebView2...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=Get-AuthenticodeSignature 'dist\prerequisites\MicrosoftEdgeWebView2RuntimeInstallerX64.exe'; if($s.Status -ne 'Valid' -or $s.SignerCertificate.Subject -notmatch 'Microsoft'){throw 'Signature Microsoft WebView2 invalide'}"
if errorlevel 1 goto :error
echo Verification de la syntaxe des scripts PowerShell et des assets terminee.
echo [4/5] Compilation WinForms + WebView2...
REM Clear old build output to prevent stale artifacts from passing validation.
if exist "dist\windows-x64" rmdir /s /q "dist\windows-x64"
if exist "dist\windows-x64" goto :error
if exist "dist\installer\OpenVisio-Setup-v41.77-x64.exe" del /q "dist\installer\OpenVisio-Setup-v41.77-x64.exe"
"%DOTNET_ROOT%\dotnet.exe" publish "windows\native\OpenVisio.csproj" -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o "dist\windows-x64"
if errorlevel 1 goto :error
if not exist "dist\windows-x64\OpenVisio.exe" goto :error
if not exist "dist\windows-x64\wwwroot\index.html" goto :error
if not exist "dist\windows-x64\wwwroot\src\main.js" goto :error
if not exist "dist\windows-x64\wwwroot\styles\app.css" goto :error
echo [5/5] Compilation installateur...
"%ISCC%" "windows\installer\OpenVisio.iss"
if errorlevel 1 goto :error
if not exist "dist\installer\OpenVisio-Setup-v41.77-x64.exe" goto :error
echo Verification de la taille du livrable...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='dist\installer\OpenVisio-Setup-v41.77-x64.exe'; if((Get-Item $p).Length -lt 1000000){throw 'Installateur anormalement petit'}"
if errorlevel 1 goto :error
echo [POST] Construction de la distribution portable...
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Build-Portable-Windows.ps1"
if errorlevel 1 goto :error
if not exist "dist\portable\OpenVisio-v41.77-Windows-x64-Portable.exe" goto :error
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Stage-Binaries.ps1"
if errorlevel 1 goto :error
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Write-Release-Manifest.ps1"
if errorlevel 1 goto :error
echo SUCCES: dist\installer\OpenVisio-Setup-v41.77-x64.exe
powershell -NoProfile -Command "Get-FileHash 'dist\installer\OpenVisio-Setup-v41.77-x64.exe' -Algorithm SHA256 | Format-List"
exit /b 0
:error
echo ECHEC: construction interrompue. Verifiez la connexion Internet, les droits et les messages precedents.
exit /b 1
