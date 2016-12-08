@echo off
endlocal & setlocal EnableDelayedExpansion

set name=spsvc
set dst=%~dp0
set psexec=%dst%\psexec.exe

for /f "tokens=2,4 delims=," %%a in ('tasklist /fi "imagename eq winlogon.exe" /fo csv /nh') do call:run %%a %%b

goto:end

:run
	set /A ppid=(%~1+0)
	set /A sess=(%~2+0)
	if "%ppid%"=="0" exit /b
	for /f "tokens=2,4 delims=," %%a in ('tasklist /fi "imagename eq %name%.exe" /fi "session eq %sess%" /fo csv /nh') do ( 
		set /A apid=%%~a+0
		@echo "!apid!"
		if not "!apid!"=="0" exit /b 
	)
	%psexec% -accepteula -d -i %sess% %dst%\%name%.exe
	exit /b
	
:end
	
	REM exit 0