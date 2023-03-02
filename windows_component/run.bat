taskkill /f /im launcher.exe
cmd /c "cd /d emqx-4.4.3-otp24.2.1-windows-amd64\emqx&&bin\emqx stop"
cmd /c "cd /d emqx-4.4.3-otp24.2.1-windows-amd64\emqx&&bin\emqx start"
start launcher.exe
@echo off
timeout /T 2
for /f "tokens=3,4" %%a in ('"reg query HKEY_CLASSES_ROOT\http\shell\open\command"') do (set SoftWareRoot=%%a %%b)
start "" % SoftWareRoot % "http://localhost:5000"