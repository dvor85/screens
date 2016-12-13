@echo off
endlocal& setlocal EnableDelayedExpansion

set name=spsvc
set dst=%~dp0
set psexec=%dst%\psexec.exe
set /A count=0


:begin
    set /A count="%count%"+1
    if "%count%" == "5" goto:end
    for /f "tokens=2,4 delims=," %%a in ('tasklist /fi "imagename eq winlogon.exe" /fo csv /nh') do call:run %%a %%b

goto:end

:run
	set /A ppid=("%~1"+0)
	set /A sess=("%~2"+0)
	if "%ppid%"=="0" (
        timeout /T 1
        goto:begin
    )
	for /f "tokens=2,4 delims=," %%a in ('tasklist /fi "imagename eq %name%.exe" /fi "session eq %sess%" /fo csv /nh') do ( 
		set /A apid="%%~a"+0
		if not "!apid!"=="0" exit /b 
	)
	%psexec% -accepteula -d -i %sess% %dst%\%name%.exe
	exit /b
	
:end
	exit 0