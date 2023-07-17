@echo off

set "VENV_NAME=myenv"

echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate

echo Virtual environment activated.

echo Running web.py...
start cmd /k python web.py

echo Opening browser...
start "" http://127.0.0.1:5000

echo Done.