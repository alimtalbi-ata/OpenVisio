@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Invoke-Windows-Release-Pipeline.ps1" %*
exit /b %ERRORLEVEL%
