cd d:\MinGW\bin\
c++.exe -O2 -static-libgcc -mwindows %~dp0\kbdsvc.cpp -o %~dp0\kbdsvc.exe
cd %~dp0
d:\progs\upx392w\upx.exe --best %~dp0\kbdsvc.exe