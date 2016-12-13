@echo off
endlocal& setlocal EnableDelayedExpansion

set self_dir=%~dp0
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=x86 || set OS=x64
ver | find /i "5." > nul && set XP=1 || set XP=0

rem Parse passed arguments to script
:parse_passed_params
  if "%~1"=="" goto:end_parse_passed_params
  if "%~1"=="install"           ( set Action="%~1" && shift & goto:parse_passed_params )
  if "%~1"=="uninstall"         ( set Action="%~1" && shift & goto:parse_passed_params )
  if "%~1"=="stop"              ( set Action="%~1" && shift & goto:parse_passed_params )
  if "%~1"=="run"               ( set Action="%~1" && shift & goto:parse_passed_params )
  if not "%~1"==""              ( set Progra="%~1" && shift & goto:parse_passed_params )
  shift & goto:parse_passed_params
:end_parse_passed_params

:begin
    if %Progra%==""        	 goto:end  
    if %Action%=="install"   call:install %Progra%
    if %Action%=="uninstall" call:uninstall %Progra%
    if %Action%=="stop"      call:stop %Progra%
    if %Action%=="run"       call:run %Progra%
    goto:end
    

:install
    if "%~1"=="" exit /b
	set name=%~1
    set dst="%ALLUSERSPROFILE%\%name%"
    set task_root=\Microsoft\Windows\%name%
    
    if "%XP%"=="1" (
        reg ADD HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /t REG_SZ /d %dst%\%name%.exe /f
        exit /b
    )    
    schtasks /Create /F /RU System /RL HIGHEST /SC ONLOGON /TN "%task_root%\%name%" /TR "%dst%\%name%.bat"
    exit /b
    
:uninstall
    if "%~1"=="" exit /b
	set name=%~1
    set dst="%ALLUSERSPROFILE%\%name%"
    set task_root=\Microsoft\Windows\%name%
    
    call:stop %name%  
    schtasks /DELETE /F /TN "%name%"
    schtasks /DELETE /F /TN "%task_root%\%name%"
    reg delete HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /f
    rmdir /Q /S "%dst%"
    exit /b
    
:stop
    if "%~1"=="" exit /b
	set name=%~1
    set dst="%ALLUSERSPROFILE%\%name%"
    set task_root=\Microsoft\Windows\%name%
    
    schtasks /END /TN "%name%"
    schtasks /END /TN "%task_root%\%name%"
    taskkill /F /IM "%name%.exe"    
    exit /b
    
:run
    if "%~1"=="" exit /b
	set name=%~1
    set dst="%ALLUSERSPROFILE%\%name%"
    set task_root=\Microsoft\Windows\%name%
    
    if "%XP%"=="1" (
        start /b "%dst%\%name%.exe"
        exit /b
    )
    schtasks /RUN /TN "%task_root%\%name%"
    exit /b
    
:end
    exit 0


