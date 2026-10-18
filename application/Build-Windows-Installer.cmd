@echo off
setlocal
cd /d "%~dp0"
call "%~dp0Build-OpenVisio-Windows.cmd"
exit /b %ERRORLEVEL%
