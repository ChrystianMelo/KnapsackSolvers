@echo off
echo Activating virtual environment...
call venv\Scripts\activate

echo Deleting previous results...
rmdir /s /q "results"
rmdir /s /q "reports"

echo Running project...
py src\main.py
pause