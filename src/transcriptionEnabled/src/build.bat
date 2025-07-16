@echo off
echo Building insta-downloader-gui...
pyinstaller --name "insta-downloader-gui" ^
  --windowed ^
  --onefile ^
  --icon=favicon.ico ^
  main.py
pause
