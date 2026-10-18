@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Qualify-Windows-Release.ps1" -RunGraphicSmoke %*
exit /b %ERRORLEVEL%
