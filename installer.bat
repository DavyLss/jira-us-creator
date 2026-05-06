@echo off
echo ============================================
echo   Jira User Story Creator - Installation
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe.
    echo Telechargez-le sur https://www.python.org/downloads/
    echo.
    echo Cochez "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

echo Python detecte. Installation des dependances...
echo.

cd /d "%~dp0"

pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERREUR lors de l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Installation terminee avec succes !
echo ============================================
echo.
echo Pour lancer l'application:
echo   - Double-cliquez sur lancer.bat
echo   - Ou executez: python main.py
echo.
pause
