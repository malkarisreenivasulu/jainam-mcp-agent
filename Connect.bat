@echo off
cd /d "%~dp0"
py -3 scripts\connect.py %*
if errorlevel 1 pause
