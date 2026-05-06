@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Jira User Story Creator - Installation
echo ========================================
echo.

:: Installation folder (no admin needed)
set "INSTALL_DIR=%LOCALAPPDATA%\jira-us-creator"
set "SRC_DIR=%~dp0"

echo [1/3] Installation dans %INSTALL_DIR%...

:: Create install directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy all files
xcopy /E /I /Q /Y "%SRC_DIR%\app.py" "%INSTALL_DIR%\"
xcopy /E /I /Q /Y "%SRC_DIR%\config.py" "%INSTALL_DIR%\"
xcopy /E /I /Q /Y "%SRC_DIR%\jira_api.py" "%INSTALL_DIR%\"
xcopy /E /I /Q /Y "%SRC_DIR%\main.py" "%INSTALL_DIR%\"
xcopy /E /I /Q /Y "%SRC_DIR%\requirements.txt" "%INSTALL_DIR%\"
:: Only copy config.json if not already installed (preserve user config)
if not exist "%INSTALL_DIR%\config.json" (
    if exist "%SRC_DIR%\config.json" xcopy /E /I /Q /Y "%SRC_DIR%\config.json" "%INSTALL_DIR%\"
)

echo [2/3] Installation des dependances Python...

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe.
    echo Telechargez-le sur https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Install dependencies with --user (no admin needed)
python -m pip install --user -r "%INSTALL_DIR%\requirements.txt"
if errorlevel 1 (
    echo ERREUR: Echec de l'installation des dependances.
    pause
    exit /b 1
)

echo [3/3] Creation du raccourci sur le bureau...

:: Create a VBScript to generate a shortcut on the desktop
set "DESKTOP=%USERPROFILE%\Desktop"
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%DESKTOP%\Jira US Creator.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "cmd.exe" >> "%VBS_SCRIPT%"
echo oLink.Arguments = "/c pythonw ""%INSTALL_DIR%\main.py""" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%VBS_SCRIPT%"
echo oLink.WindowStyle = 7 >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

cscript //nologo "%VBS_SCRIPT%"
del /Q "%VBS_SCRIPT%"

echo.
echo ========================================
echo  Installation terminee avec succes !
echo ========================================
echo.
echo Un raccourci "Jira US Creator" a ete cree sur votre bureau.
echo.
echo Vous pouvez aussi lancer l'app manuellement avec:
echo %INSTALL_DIR%\lancer.bat
echo.
pause
