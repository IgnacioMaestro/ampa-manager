# AMPA Manager

## Diagrama del modelo del dominio
[Diagrama del modelo del dominio](doc/DomainModelDiagram/DomainModelDiagram.md)

## Diagramas de casos de uso
[Diagramas de casos de uso](doc/UseCasesDiagram/Use%20cases%20diagram.md)

## Configurar base de datos

1. Descargar fichero db.sqlite3 del drive (Ordenadores > PC AMPA > database)
1. Reemplazar ampa_members_manager_project\database\db.sqlite3
1. Realizar modificaciones
1. Subir el fichero al drive (Ordenadores > PC AMPA > database)

## Traducciones

1. Generar ficheros de traducciones

```
django-admin makemessages -l es -l eu
python manage.py makemessages -l es
```

2. Completar las traducciones
   1. Validar traducciones marcadas como "fuzzy" (son traducciones automáticas basadas en textos similares). Una vez validadas se les puede quitar la etiqueta "fuzzy".
   2. Completar traducciones pendientes (look for ``msgstr ""``)

```
locale/es/LC_MESSAGES/django.po 
locale/eu/LC_MESSAGES/django.po
```

3. Compilar ficheros de traducciones

```
django-admin compilemessages
```

## Importar desde un fichero excel

- Familia: se filtra por apellidos
- Padres: se filtra por nombre y apellidos
- Cuenta bancaria: se filtra por IBAN.
- Hijo: se filtra por nombre y familia

En todos los casos si existe se actualiza, si no se crea. Si hubiera varias elementos que cumplen el filtro no se procesa y se muestra un aviso.

```
python manage.py import <FILE_PATH>
```

## Borrar ficheros del historial

1. Instalar [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
2. Ejecutar en una nueva carpeta

```
git clone --mirror https://github.com/IgnacioMaestro/ampa-manager.git
java -jar .\bfg-1.14.0.jar --delete-files '<FILE TO REMOVE>' .\ampa-manager.git\
cd .\ampa-manager.git\
$ git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push
```
