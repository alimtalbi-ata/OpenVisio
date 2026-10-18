@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Qualify-Windows-Release.ps1"
exit /b %ERRORLEVEL%
