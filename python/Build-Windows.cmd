@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1 || (echo Python 3.12 required & exit /b 1)
py -3.12 -m venv .venv || exit /b 1
call .venv\Scripts\activate.bat || exit /b 1
python -m pip install --upgrade pip || exit /b 1
python -m pip install -r requirements-build.txt || exit /b 1
set PYTHONPATH=%CD%
python -m unittest discover -s tests -v || exit /b 1
python -m PyInstaller --noconfirm --clean --onefile --windowed --name OpenVisio-v42.0-Windows-x64-Portable --paths . openvisio\__main__.py || exit /b 1
if not exist binary mkdir binary
copy /y dist\OpenVisio-v42.0-Windows-x64-Portable.exe binary\ || exit /b 1
echo SUCCESS: binary\OpenVisio-v42.0-Windows-x64-Portable.exe
