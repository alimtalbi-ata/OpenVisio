@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
where py >nul 2>&1 || (echo Python 3.12 required & exit /b 1)
py -3.12 -m venv .venv || exit /b 1
call .venv\Scripts\activate.bat || exit /b 1
python -m pip install --upgrade pip || exit /b 1
python -m pip install -r requirements-build.txt || exit /b 1
python -m pip install python-docx reportlab || exit /b 1
set PYTHONPATH=%CD%
python -m unittest discover -s tests -v || exit /b 1
python -m PyInstaller --noconfirm --clean --onefile --windowed --name OpenVisio-v42.0-Windows-x64-Portable --paths . run_openvisio.py || exit /b 1
if not exist binary mkdir binary
copy /y dist\OpenVisio-v42.0-Windows-x64-Portable.exe binary\ || exit /b 1
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not exist "!ISCC!" set "ISCC=%%I"
if not exist "%ISCC%" (echo Inno Setup 6 required & exit /b 1)
"%ISCC%" "installer\OpenVisio-Python.iss" || exit /b 1
python scripts\generate_docs.py || exit /b 1
python scripts\package_release.py || exit /b 1
echo SUCCESS: installer, portable, documentation, ZIP
