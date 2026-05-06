@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Build - Jira User Story Creator
echo ========================================
echo.

:: Go to script directory
cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe.
    pause
    exit /b 1
)

:: Install PyInstaller if needed
echo [1/2] Verification de PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installation de PyInstaller...
    python -m pip install --user pyinstaller
)

:: Clean old builds
echo [2/2] Compilation en cours...
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"
if exist "*.spec" del /Q "*.spec"

:: Build single file executable
python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name "Jira US Creator" ^
    main.py

if errorlevel 1 (
    echo.
    echo ERREUR: La compilation a echoue.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build termine avec succes !
echo ========================================
echo.
echo L'executable est disponible dans: dist\Jira US Creator.exe
echo.
echo Pour distribuer: copiez ce fichier .exe a l'utilisateur.
echo Il peut le placer ou il veut et le lancer directement.
echo.
echo Note: Le fichier config.json sera cree automatiquement
echo dans %%LOCALAPPDATA%%\jira-us-creator\ au premier lancement.
echo.
pause
