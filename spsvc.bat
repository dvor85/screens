@echo off
endlocal& setlocal EnableDelayedExpansion

set name=spsvc
set dst=%~dp0
set psexec="%dst%\psexec.exe"
set logonsessions="%dst%\logonsessions.exe"


:begin
    for /f "tokens=4,5 delims=," %%a in ('%logonsessions% -accepteula -c') do (	
		set stype=%%a
		set inter=!stype:Interactive=!
		if not "!inter!"=="!stype!" echo call:run %%~b	
	)
	rem if loop above is fail then return errorlevel is 0 else errorlevel is pid of runned process
	if "%ERRORLEVEL%"=="0" call:run
	
	goto:end
	
:run	
	rem set /A sess=("%~1"+0)	
	set sess=%~1
	%psexec% -accepteula -d -i %sess% "%dst%\%name%.exe"
	exit /b
	
:end
	exit 0