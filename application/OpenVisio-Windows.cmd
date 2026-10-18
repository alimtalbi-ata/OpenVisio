@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\openvisio.ps1" %*
if errorlevel 1 (
 echo.
 echo OpenVisio could not start. Check the message above.
 pause
)
endlocal
