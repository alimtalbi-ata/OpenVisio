@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (echo Python introuvable. & exit /b 2)
py -3 -c "import playwright" >nul 2>&1
if errorlevel 1 (echo Installer Playwright : py -3 -m pip install playwright & exit /b 2)
if not exist "recette" mkdir "recette"
py -3 tests\browser-recovery.py --report "recette\rapport.json" --screenshot "recette\capture.png" %*
if errorlevel 1 (echo ECHEC : consulter recette\rapport.json & exit /b 1)
echo SUCCES : recette\rapport.json et recette\capture.png
