@echo off
echo AstroExpert launcher
echo This opens backend and frontend in separate PowerShell windows.
start "AstroExpert Backend" powershell -NoExit -Command "cd '%~dp0backend'; if (!(Test-Path venv)) { py -m venv venv }; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload"
start "AstroExpert Frontend" powershell -NoExit -Command "cd '%~dp0frontend'; npm install; npm run dev"
