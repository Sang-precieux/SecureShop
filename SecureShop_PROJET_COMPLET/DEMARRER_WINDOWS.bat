@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "env\Scripts\python.exe" (
  echo Vous devez d'abord lancer INSTALLER_WINDOWS.bat.
  pause
  exit /b 1
)
call "env\Scripts\activate.bat"
echo Boutique client   : http://127.0.0.1:8000/
echo Administration    : http://127.0.0.1:8000/accounts/admin-login/
echo Les OTP s'affichent ici si Gmail n'est pas configure.
echo Pour arreter : CTRL+C
python manage.py runserver
pause
