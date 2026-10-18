@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0windows\openvisio_server.py" %*
  goto :end
)
where python >nul 2>nul
if not errorlevel 1 (
  python "%~dp0windows\openvisio_server.py" %*
  goto :end
)
echo Python 3 not found. Install Python 3 from python.org and retry.
echo No administrator privileges or pip packages are required.
pause
:end
endlocal
