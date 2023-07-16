@echo off

:venv
echo Executing: pip install virtualenv
call python -m pip install virtualenv

echo Checking: venv\
if NOT exist venv\ (
    echo WARN: venv\ not exist, creating
    call python -m virtualenv venv
)

echo Entering virtualenv
call .\venv\Scripts\activate.bat
if NOT %ERRORLEVEL% == 0 (
    echo Probably virtualenv is corrupted. Try to delete the `venv` folder, then run the script again.
    goto :error
)


:requirements
echo Executing: pip install -r requirements.txt
call python -m pip install -r requirements.txt


:bot_start
echo Starting bot...
timeout 2 > NUL

cls
call python atlb

:error
exit