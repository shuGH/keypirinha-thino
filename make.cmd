@echo off
setlocal

set PACKAGE_NAME=Thino
REM set INSTALL_DIR=%APPDATA%\Keypirinha\InstalledPackages
set INSTALL_DIR=C:\Applications\Keypirinha\portable\Profile\InstalledPackages
set LIVEPACKAGES_DIR=C:\Applications\Keypirinha\portable\Profile\Packages
set KEYPIRINHA_SDK_DIR=..\Sdk

if "%1"=="" goto help
if "%1"=="-h" goto help
if "%1"=="--help" goto help
if "%1"=="help" goto help
goto command

:help
echo Usage:
echo   make help              : Show this help message
echo   make clean             : Remove the build output directory
echo   make build             : Build the Keypirinha package (includes LICENSE*, README*, and src)
echo   make install           : Copy the built .keypirinha-package to InstalledPackages
echo   make live              : Create a junction in Keypirinha LivePackages
echo   make unlive            : Remove the LivePackages junction
echo   make py [python_args]  : Run the Keypirinha SDK Python environment (kpy)
echo   make env               : Set up the Keypirinha SDK environment
echo   make deploy            : Run build and install
goto end

:command
if "%1"=="env" (
    pushd "%~dp0"
    call "%KEYPIRINHA_SDK_DIR%\cmd\kpenv.cmd"
    popd
    goto end
)

if "%1"=="live" (
    if not exist "%LIVEPACKAGES_DIR%" mkdir "%LIVEPACKAGES_DIR%"

    if exist "%LIVEPACKAGES_DIR%\%PACKAGE_NAME%" (
        echo ERROR: Live package already exists:
        echo   "%LIVEPACKAGES_DIR%\%PACKAGE_NAME%"
        exit /b 1
    )

    mklink /J "%LIVEPACKAGES_DIR%\%PACKAGE_NAME%" "%~dp0src"
    goto end
)

if "%1"=="unlive" (
    if not exist "%LIVEPACKAGES_DIR%\%PACKAGE_NAME%" (
        echo Live package junction does not exist:
        echo   "%LIVEPACKAGES_DIR%\%PACKAGE_NAME%"
        goto end
    )

    rmdir "%LIVEPACKAGES_DIR%\%PACKAGE_NAME%"
    goto end
)

if "%BUILD_DIR%"=="" set BUILD_DIR=%~dp0build
if "%KEYPIRINHA_SDK_DIR%"=="" (
    echo ERROR: Keypirinha SDK environment not setup.
    echo        Run SDK's "kpenv" script and try again.
    exit /b 1
)

if "%1"=="clean" (
    if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
    goto end
)

if "%1"=="build" (
    if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
    pushd "%~dp0"
    call "%KEYPIRINHA_SDK_DIR%\cmd\kparch" ^
        "%BUILD_DIR%\%PACKAGE_NAME%.keypirinha-package" ^
        -r LICENSE* README* src
    popd
    goto end
)

if "%1"=="install" (
    REM echo TODO: ensure the INSTALL_DIR variable declared at the top of this
    REM echo       script complies to your configuration and remove this message
    REM exit /1

    copy /Y "%BUILD_DIR%\*.keypirinha-package" "%INSTALL_DIR%\"
    goto end
)

if "%1"=="dev" (
    if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
    pushd "%~dp0"
    call "%KEYPIRINHA_SDK_DIR%\cmd\kparch" ^
        "%BUILD_DIR%\%PACKAGE_NAME%.keypirinha-package" ^
        -r LICENSE* README* src
    popd

    echo TODO: ensure the INSTALL_DIR variable declared at the top of this
    echo       script complies to your configuration and remove this message
    exit /1

    copy /Y "%BUILD_DIR%\*.keypirinha-package" "%INSTALL_DIR%\"
    goto end
)

if "%1"=="py" (
    call "%KEYPIRINHA_SDK_DIR%\cmd\kpy" %2 %3 %4 %5 %6 %7 %8 %9
    goto end
)

if "%1"=="deploy" (
    call %0 build
    call %0 install
    goto end
)

:end
