@echo off
echo Building Instagram Media Downloader...
pyinstaller --name "IMD" ^
  --windowed ^
  --onefile ^
  --icon=favicon.ico ^
  main.py
pause
