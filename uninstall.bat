@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Jira User Story Creator - Desinstallation
echo ========================================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\jira-us-creator"

:: Check if installed
if not exist "%INSTALL_DIR%" (
    echo Aucune installation trouvee dans %INSTALL_DIR%.
    pause
    exit /b 0
)

echo [1/2] Suppression du raccourci bureau...
set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%\Jira US Creator.lnk" del /F /Q "%DESKTOP%\Jira US Creator.lnk"
if exist "%DESKTOP%\JiraUSCreator.lnk" del /F /Q "%DESKTOP%\JiraUSCreator.lnk"

echo [2/2] Suppression des fichiers...
rmdir /S /Q "%INSTALL_DIR%"

echo.
echo ========================================
echo  Desinstallation terminee.
echo ========================================
echo.
pause
