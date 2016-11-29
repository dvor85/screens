@echo off
endlocal & setlocal EnableDelayedExpansion

set self_dir=%~dp0

rem Parse passed arguments to script
:parse_passed_params
  if "%~1"=="" goto:end_parse_passed_params
  if "%~1"=="install"           ( set Action="%~1" && shift & goto:parse_passed_params )
  if "%~1"=="uninstall"         ( set Action="%~1" && shift & goto:parse_passed_params )
  if "%~1"=="stop"              ( set Action="%~1" && shift & goto:parse_passed_params )
  if "%~1"=="run"               ( set Action="%~1" && shift & goto:parse_passed_params )
  if not "%~1"==""              ( set Name="%~1" && shift & goto:parse_passed_params )
  shift & goto:parse_passed_params
:end_parse_passed_params

:begin
    if %Action%=="install"   call:install %Name%
    if %Action%=="uninstall" call:uninstall %Name%
    if %Action%=="stop"      call:stop %Name%
    if %Action%=="run"       call:run %Name%
    goto:end

:install
    set name=%~1
    if "%name%"=="" exit /b
    set dst_dir="%ALLUSERSPROFILE%\%name%"
    reg ADD HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /t REG_SZ /d %dst_dir%\%name%.exe /f 
    schtasks /Create /F /RU System /RL HIGHEST /SC ONSTART /TN "%name%" /TR "%dst_dir%\%name%.exe" || schtasks /Create /RU System /SC ONSTART /TN "%name%" /TR "%dst_dir%\%name%.exe"
    ping -4 -w 100 -n 1 spagent.capital.co && set loc=1 || set loc=0
    if %loc%==0 del /F /Q "%dst_dir%\config.bin"
    exit /b
    
:uninstall
    set name=%~1
    if "%name%"=="" exit /b
    set dst_dir="%ALLUSERSPROFILE%\%name%"
    call:stop %name%
    schtasks /DELETE /F /TN "%name%"
    reg delete HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /f
    del /F /Q /S "%dst_dir%"
    exit /b
    
:stop
    set name=%~1
    if "%name%"=="" exit /b
    schtasks /END /TN "%name%"
    taskkill /F /IM "%name%.exe"    
    exit /b
    
:run
    set name=%~1
    if "%name%"=="" exit /b
    schtasks /RUN /TN "%name%"      
    exit /b
    
:end
    REM del /F /Q "%0"


