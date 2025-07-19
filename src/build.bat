@echo off
echo Building insta-downloader-gui...
pyinstaller --name "insta-downloader-gui" ^
  --windowed ^
  --icon=favicon.ico ^
  --add-data "whisper/assets;whisper/assets" ^
  main.py
pause
