@echo off
setlocal

: Set the script directory to the location of this batch file
set SCRIPT_DIR=%~dp0

: Start ZenNotes
echo Starting ZenNotes...
python "%SCRIPT_DIR%src\main.py"
echo Exiting...

endlocal