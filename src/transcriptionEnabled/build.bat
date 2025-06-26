@echo off
echo Building Instagram Media Downloader...
pyinstaller --name "IMD" ^
  --windowed ^
  --icon=favicon.ico ^
  main.py
pause
