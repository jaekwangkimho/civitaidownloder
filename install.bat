@echo off

set "VENV_NAME=myenv"

echo Creating virtual environment...
python -m venv %VENV_NAME%

echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate

echo Installing required packages...

REM requirements.txt 파일을 한 줄씩 읽어서 패키지 설치
for /f "tokens=*" %%i in (requirements.txt) do (
    echo Installing %%i
    pip install %%i
)

echo Done.

echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate

pause
