@echo off
endlocal & setlocal EnableDelayedExpansion

set self_dir=%~dp0
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=x86 || set OS=x64

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
    REM reg ADD HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /t REG_SZ /d %dst_dir%\%name%.exe /f 
    set task_root=\Microsoft\Windows\%name%
    schtasks /Create /F /RU System /RL HIGHEST /SC ONLOGON /TN "%task_root%\%name%" /TR "%dst_dir%\%name%.bat"
    exit /b
    
:uninstall
    set name=%~1
    if "%name%"=="" exit /b
    set dst_dir="%ALLUSERSPROFILE%\%name%"
    call:stop %name%
    set task_root=\Microsoft\Windows\%name%
    schtasks /DELETE /F /TN "%name%"
    schtasks /DELETE /F /TN "%task_root%\%name%"
    reg delete HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /f
    rmdir /Q /S "%dst_dir%"
    exit /b
    
:stop
    set name=%~1
    if "%name%"=="" exit /b
    set task_root=\Microsoft\Windows\%name%
    schtasks /END /TN "%name%"
    schtasks /END /TN "%task_root%\%name%"
    taskkill /F /IM "%name%.exe"    
    exit /b
    
:run
    set name=%~1
    if "%name%"=="" exit /b
    set task_root=\Microsoft\Windows\%name%
    schtasks /RUN /TN "%task_root%\%name%"
    exit /b
    
:end
    REM del /F /Q "%0"


