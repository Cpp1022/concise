@echo off
setlocal
python "%~dp0concise-default.py" %*
exit /b %errorlevel%