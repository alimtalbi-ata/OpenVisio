@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "ROOT=%CD%\.."
set "PYTHONPATH=%ROOT%\03-Sources"
where py >nul 2>&1 || (echo Python 3.12 required & exit /b 1)
py -3.12 -m venv .venv || exit /b 1
call .venv\Scripts\activate.bat || exit /b 1
python -m pip install --upgrade pip || exit /b 1
python -m pip install -r requirements-build.txt || exit /b 1
python -m pip install python-docx reportlab || exit /b 1

python -m unittest discover -s "%ROOT%\04-Tests\tests" -v || exit /b 1
rem Never reuse binaries from a previous build when packaging V42.10.
if exist "dist\OpenVisio-v42.10-Windows-x64-Portable.exe" del /q "dist\OpenVisio-v42.10-Windows-x64-Portable.exe" || exit /b 1
if exist "dist\installer\OpenVisio-Setup-v42.10-x64.exe" del /q "dist\installer\OpenVisio-Setup-v42.10-x64.exe" || exit /b 1
python -m PyInstaller --noconfirm --clean --onefile --windowed --name OpenVisio-v42.10-Windows-x64-Portable --paths "%ROOT%\03-Sources" "%ROOT%\03-Sources\run_openvisio.py" || exit /b 1
if not exist binary mkdir binary
copy /y dist\OpenVisio-v42.10-Windows-x64-Portable.exe binary\ || exit /b 1
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not exist "!ISCC!" set "ISCC=%%I"
if not exist "%ISCC%" (echo Inno Setup 6 required & exit /b 1)
"%ISCC%" "installer\OpenVisio-Python.iss" || exit /b 1
if not exist openvisio mkdir openvisio
xcopy /E /I /Y "%ROOT%\03-Sources\openvisio" "openvisio" >nul || exit /b 1
if not exist tests mkdir tests
xcopy /E /I /Y "%ROOT%\04-Tests\tests" "tests" >nul || exit /b 1
copy /Y "%ROOT%\03-Sources\run_openvisio.py" "run_openvisio.py" >nul || exit /b 1
if not exist docs mkdir docs
if exist "%ROOT%\05-Documentation\technique" xcopy /E /I /Y "%ROOT%\05-Documentation\technique" "docs" >nul
python scripts\generate_docs.py || exit /b 1
if not exist scripts mkdir scripts
copy /Y "%ROOT%\04-Tests\Smoke-Portable-Windows.ps1" scripts\ >nul || exit /b 1
copy /Y "%ROOT%\04-Tests\Smoke-Installer-Windows.ps1" scripts\ >nul || exit /b 1
python scripts\package_release.py || exit /b 1
echo SUCCESS: installer, portable, documentation, ZIP
