@echo off
setlocal enabledelayedexpansion
echo ====================================================
echo            SBM AUTOMATED INSTALLER
echo ====================================================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\sbm-tools"

if not exist "%INSTALL_DIR%" (
    echo [+] Creating installation folder at %INSTALL_DIR%...
    mkdir "%INSTALL_DIR%"
) else (
    echo [*] Installation folder already exists. Updating files...
)

echo [+] Copying compiler scripts...
if exist "sbm.py" copy /Y "sbm.py" "%INSTALL_DIR%\" >nul
if exist "sbm2png.py" copy /Y "sbm2png.py" "%INSTALL_DIR%\" >nul

echo [+] Generating global terminal command wrappers...

(
echo @echo off
echo python "%INSTALL_DIR%\sbm.py" %%*
) > "%INSTALL_DIR%\sbm.bat"

(
echo @echo off
echo python "%INSTALL_DIR%\sbm2png.py" %%*
) > "%INSTALL_DIR%\sbm2png.bat"

echo [+] Registering global environment path...
echo %PATH% | findstr /I /C:"%INSTALL_DIR%" >nul
if %errorlevel% neq 0 (
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH') do set "OLD_PATH=%%B"
    setx PATH "%INSTALL_DIR%;!OLD_PATH!" >nul
    echo [SUCCESS] Added %INSTALL_DIR% to your system PATH.
) else (
    echo [*] %INSTALL_DIR% is already registered in your system PATH.
)

echo.
echo ====================================================
echo SBM Installation complete!
echo Please restart your terminal window to apply changes.
echo You can now run 'sbm' or 'sbm2png'.
echo ====================================================
pause