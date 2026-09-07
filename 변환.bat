@echo off
chcp 65001 >nul
rem 녹음 파일을 이 배치파일 위에 드래그&드롭하면 변환됩니다.
setlocal
set "HERE=%~dp0"
if "%~1"=="" (
  echo 사용법: 녹음 파일을 이 파일 위로 드래그해서 놓으세요.
  echo    또는: 변환.bat "C:\경로\녹음.m4a"
  pause
  exit /b 1
)
"%HERE%.venv\Scripts\python.exe" "%HERE%transcribe.py" %*
echo.
pause
