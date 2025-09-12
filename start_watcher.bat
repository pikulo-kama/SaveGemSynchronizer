@echo off
:loop

:: Wait before checking.
timeout /t 180 /nobreak >nul

:: Check if process is running
tasklist /fi "IMAGENAME eq ProcessWatcher.exe" | find /i "ProcessWatcher.exe" >nul

if ERRORLEVEL 1 (
    :: Start the watcher
    start "" /b "%~dp0ProcessWatcher.exe"
)

goto loop
