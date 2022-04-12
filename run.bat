taskkill /f /im launcher.exe
cmd /c "cd /d emqx-4.4.1-otp23.0-windows-amd64_\emqx&&bin\emqx start"
start launcher.exe
@echo off
timeout /T 2
for /f "tokens=3,4" %%a in ('"reg query HKEY_CLASSES_ROOT\http\shell\open\command"') do (set SoftWareRoot=%%a %%b)
start "" % SoftWareRoot % "http://localhost:5000"