@echo off
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Erreur lors du lancement. Appuyez sur une touche...
    pause
)
