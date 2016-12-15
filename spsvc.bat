@echo off
endlocal& setlocal EnableDelayedExpansion

set name=spsvc
set dst=%~dp0
set psexec="%dst%\psexec.exe"


:begin
	for /f %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\SessionData" /f * /k ^| find /i "HKEY_LOCAL_MACHINE"') do call:run %%~na
	rem if loop above is fail then return errorlevel is 0 else errorlevel is pid of runned process
	if "%ERRORLEVEL%"=="0" call:run
	
	goto:end
	
:run	
	set /A sess=("%~1"+0)	
	for /f "tokens=2,4 delims=," %%a in ('tasklist /fi "imagename eq %name%.exe" /fi "session eq %sess%" /fo csv /nh') do ( 
		set /A apid="%%~a"+0
		if not "!apid!"=="0" exit /b 1
	)
	%psexec% -accepteula -d -i %sess% "%dst%\%name%.exe"
	exit /b
	
:end
	exit 0