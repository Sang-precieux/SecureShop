@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "env\Scripts\python.exe" (
  echo Lancez d'abord INSTALLER_WINDOWS.bat.
  pause
  exit /b 1
)
call "env\Scripts\activate.bat"
echo IMPORTANT : donnez une adresse e-mail valide pour recevoir l'OTP en mode Gmail.
echo En mode demonstration, le code OTP apparait dans le terminal du serveur.
python manage.py createsuperuser
pause
