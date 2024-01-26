@echo off
setlocal
title AMPA. Mantener abierto para usar la aplicacion

chcp 65001 > nul

:: DEFINIR RUTAS
set "REPO_PATH=C:\ampa-manager"
set "PYTHON_PATH=C:\Users\abend\AppData\Local\Programs\Python\Python311\python"
set "DJANGO_MANAGE_PATH=%REPO_PATH%\software_components\app_server\ampa_members_manager_project\manage.py"
set "DB_FOLDER_PATH=%REPO_PATH%\software_components\app_server\ampa_members_manager_project\database\"
set "DB_FILE_WITHOUT_EXT=db"
set "DB_FILE_EXT=.sqlite3"
set "DB_FILE=%DB_FILE_WITHOUT_EXT%%DB_FILE_EXT%"
set "DB_BACKUPS_FOLDER_NAME=backups"
set "DB_BACKUPS_PATH=%DB_FOLDER_PATH%%DB_BACKUPS_FOLDER_NAME%\"

echo Eliminando archivos .%DB_FILE_EXT% con tamaño 0 en %DB_FOLDER_PATH%
for %%I in ("%DB_FOLDER_PATH%\*.%DB_FILE_EXT%") do (
    echo Analizando archivo: %%I
    if %%~zI equ 0 (
        echo Eliminando archivo: %%I
        del "%%I"
    )
)

echo ------------------------------------------------------------
echo Renombrando archivos de base de datos con tamaño mayor que 0
for %%I in ("%DB_FOLDER_PATH%\*.%DB_FILE_EXT%") do (
    if not %%~zI equ 0 (
        echo Renombrando archivo: %%I
        ren "%%I" "%DB_FILE_WITHOUT_EXT%.%%DB_FILE_EXT%"
    )
)

echo ------------------------------------------------------------
echo Creando copia de la base de datos
if not exist "%DB_BACKUPS_PATH%" mkdir "%DB_BACKUPS_PATH%"
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "datetime=%%a"
set "DATE_TIME=%datetime:~0,8%_%datetime:~8,6%"
set FILE_SOURCE=%DB_FOLDER_PATH%%DB_FILE%
set FILE_TARGET=%DB_BACKUPS_PATH%%DB_FILE_WITHOUT_EXT%_%DATE_TIME%%DB_FILE_EXT%
copy "%FILE_SOURCE%" "%FILE_TARGET%"

echo ------------------------------------------------------------
echo Accediendo a la carpeta de la aplicacion
cd %REPO_PATH%

echo ------------------------------------------------------------
echo Actualizando aplicacion
git pull

echo ------------------------------------------------------------
echo Iniciando aplicacion (NO CIERRES ESTA VENTANA)
%PYTHON_PATH% %DJANGO_MANAGE_PATH% runserver 

endlocal