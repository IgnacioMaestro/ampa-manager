@echo off
title AMPA. Mantener abierto para usar la aplicacion

:: DEFINIR RUTAS
set "REPO_PATH=C:\Users\danil\OneDrive\Documents\ampa-manager"
set "PYTHON_PATH=%REPO_PATH%\software_components\app_server\ampa_members_manager_project\venv\Scripts\python"
set "DJANGO_MANAGE_PATH=%REPO_PATH%\software_components\app_server\ampa_members_manager_project\manage.py"

echo Accediendo a la carpeta de la aplicacion
cd %REPO_PATH%

echo Actualizando aplicacion
git pull

echo Iniciando aplicacion (NO CIERRES ESTA VENTANA)
%PYTHON_PATH% %DJANGO_MANAGE_PATH% runserver 
