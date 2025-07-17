@echo off
echo Building insta-downloader-gui...
pyinstaller --name "insta-downloader-gui" ^
  --windowed ^
  --icon=favicon.ico ^
  --add-data "favicon.ico;." ^
  --add-data "whisper;whisper" ^
  --add-data "bin;bin" ^
  --hidden-import "whisper" ^
  --hidden-import "whisper.model" ^
  --hidden-import "whisper.decoding" ^
  --hidden-import "numpy" ^
  --hidden-import "torch" ^
  main.py
pause
