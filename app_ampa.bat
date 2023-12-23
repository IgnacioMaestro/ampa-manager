@echo off
title AMPA. Mantener abierto para usar la aplicacion

:: DEFINIR RUTAS
set "REPO_PATH=C:\Users\danil\OneDrive\Documents\ampa-manager"
set "PYTHON_PATH=%REPO_PATH%\software_components\app_server\ampa_members_manager_project\venv\Scripts\python"
set "DJANGO_MANAGE_PATH=%REPO_PATH%\software_components\app_server\ampa_members_manager_project\manage.py"
set "DB_PATH=%REPO_PATH%\software_components\app_server\ampa_members_manager_project\database\"
set "DB_FILE_WITHOUT_EXT=db"
set "DB_FILE_EXT=.sqlite3"
set "DB_FILE=%DB_FILE_WITHOUT_EXT%%DB_FILE_EXT%"
set "DB_BACKUPS_FOLDER_NAME=backups"
set "DB_BACKUPS_PATH=%DB_PATH%%DB_BACKUPS_FOLDER_NAME%\"

echo Creando copia de la base de datos
if not exist "%DB_BACKUPS_PATH%" mkdir "%DB_BACKUPS_PATH%"
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "datetime=%%a"
set "DATE_TIME=%datetime:~0,8%_%datetime:~8,6%"
set FILE_SOURCE=%DB_PATH%%DB_FILE%
set FILE_TARGET=%DB_BACKUPS_PATH%%DB_FILE_WITHOUT_EXT%_%DATE_TIME%%DB_FILE_EXT%
copy "%FILE_SOURCE%" "%FILE_TARGET%"

echo Accediendo a la carpeta de la aplicacion
cd %REPO_PATH%

echo Actualizando aplicacion
git pull

echo Iniciando aplicacion (NO CIERRES ESTA VENTANA)
%PYTHON_PATH% %DJANGO_MANAGE_PATH% runserver 
