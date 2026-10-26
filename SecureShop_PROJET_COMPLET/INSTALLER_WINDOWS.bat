@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===============================================
echo  SECURESHOP - INSTALLATION AUTOMATIQUE
echo ===============================================
if not exist "env\Scripts\python.exe" (
  echo Creation de l'environnement Python...
  py -3 -m venv env
  if errorlevel 1 python -m venv env
  if errorlevel 1 goto erreur
)
call "env\Scripts\activate.bat"
echo Installation des dependances Django...
python -m pip install -r requirements.txt
if errorlevel 1 goto erreur
echo Configuration locale des cles privees...
python initialiser_config.py
if errorlevel 1 goto erreur
echo Preparation de la base de donnees...
python manage.py makemigrations accounts shop payments
if errorlevel 1 goto erreur
python manage.py migrate
if errorlevel 1 goto erreur
python manage.py seed_products
if errorlevel 1 goto erreur
python manage.py check
if errorlevel 1 goto erreur
echo.
echo Installation terminee !
echo 1 - Double-cliquez DEMARRER_WINDOWS.bat
echo 2 - Ouvrez http://127.0.0.1:8000/
echo 3 - Creez un compte administrateur avec CREER_ADMIN_WINDOWS.bat
echo Note : OTP dans le terminal tant que Gmail n'est pas renseigne dans .env.
pause
exit /b 0
:erreur
echo ERREUR : consultez le message ci-dessus et le fichier LISEZ_MOI_D_ABORD.md
pause
exit /b 1
