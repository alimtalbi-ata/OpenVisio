@echo off
setlocal
cd /d "%~dp0"
where dotnet >nul 2>&1 || (echo ERREUR: SDK .NET 8 requis. & exit /b 1)
dotnet --list-sdks | findstr /r "^8\." >nul || (echo ERREUR: SDK .NET 8 introuvable. & exit /b 4)
dotnet publish "windows\native\OpenVisio.csproj" -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o "dist\windows-x64"
if errorlevel 1 exit /b 1
if not exist "dist\windows-x64\OpenVisio.exe" exit /b 2
if not exist "dist\windows-x64\wwwroot\index.html" exit /b 3
if not exist "dist\windows-x64\wwwroot\src" exit /b 5
echo OpenVisio.exe construit. Le runtime Microsoft Edge WebView2 doit etre present sur le poste.
endlocal
