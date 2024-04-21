@echo off

python --version > nul 2>&1

if errorlevel 9009 (
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe', 'python-3.11.0-amd64.exe')"
    python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
)

python -m venv %~dp0.venv
python -m pip install aiogram==2.25.2
python -m pip install PILLOW==9.5.0
python -m pip install python-dotenv
python -m pip install sqlalchemy==1.3.24
python -m pip install mss
python -m pip install pystray
python -m pip install requests
python -m pip install pynput
python -m pip install pyinstaller
python -m pip install pythonping
python -m pip install psutil
python -m pip install sv-ttk
python -m pip install pycaw
python -m PyInstaller --onefile --noconsole --copy-metadata magic_filter -F --paths=%~dp0.venv\Lib\site-packages --icon=ico.gif --name=TPCC .\main.py

pause