@echo off
setlocal
rem Drag and drop a recording onto this file to transcribe it.
set "HERE=%~dp0"
if "%~1"=="" goto usage

"%HERE%.venv\Scripts\python.exe" "%HERE%transcribe.py" %*
echo.
pause
exit /b 0

:usage
echo 사용법: 녹음 파일을 이 파일 위로 드래그해서 놓으세요.
echo    또는: 변환.bat "C:\경로\녹음.m4a"
echo.
pause
exit /b 1
