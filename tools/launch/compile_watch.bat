@echo off
set COMPILER="C:\MinGW\bin\g++.exe"
%COMPILER% -o watch.exe launch_watch2.cpp -Wno-write-strings
