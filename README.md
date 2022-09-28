# AMPAMembersManager

## Domain model diagram
[Domain model diagram](doc/DomainModelDiagram/DomainModelDiagram.md)

## Use cases diagram
[Use cases diagram](doc/Use%20cases%20diagram.md)

## Run environment from a BAT file
1. Create virtual environment
2. Copy this to a file named run.bat.
```
@echo off
cmd /k "cd /d <PATH TO VIRTUAL ENV SCRIPTS FOLDER> & activate & cd /d <PATH TO MANAGE.PY FILE> & python manage.py runserver 0.0.0.0:8001"
```
3. Replace < PATHS >
4. Run bat file

## Create virtual environment
```
python3 -m venv /path/to/new/virtual/environment
/path/to/new/virtual/environment/Scripts/activate
pip install -r AMPAMembersManager\software_components\app_server\ampa_members_manager_project\requirements.txt
```

## Translations
1. Generate translations files

```
django-admin makemessages -l es -l eu
```

2. Edit translations files. 
   1. Check translations marked as "fuzzy" (translated automatically by django based on similar translations)
   2. Empty translations: look for ``msgstr ""``

```
locale/es/LC_MESSAGES/django.po 
locale/eu/LC_MESSAGES/django.po
```

3. Compile translations files

```
django-admin compilemessages
```

## Import from excel

- Familia: se filtra por apellidos
- Padres: se filtra por nombre y apellidos
- Cuenta bancaria: se filtra por IBAN.
- Hijo: se filtra por nombre y familia

En todos los casos si existe se actualiza, si no se crea. Si hubiera varias elementos que cumplen el filtro no se procesa y se muestra un aviso.

```
python manage.py import <FILE_PATH>

Importing file plantilla_carga_datos_familias.xls
Importing rows 2-6 from sheet "Hoja1". Rows: 7. Cols: 30
Row 2
- Family: Lopez Aguirrezabal, lopez.aguirrezabal@abendanogurasoak.com, lopezzz@gmail.com -> not_modified 
- Parent 1: Javier Lopez, +346558899, +34124578 -> not_modified 
- Parent 2: Paula Aguirrezabal, +34635241, +34698574 -> not_modified 
- Parent 1 bank account: , , False -> not_processed 
- Parent 2 bank account: ES6200752763131266485639, BSCHESMM, False -> not_modified 
- Child 1: Peio, 2012, 1 -> not_modified 
- Child 2: Beñat, 2015, 0 -> not_modified 
- Child 3: , ,  -> not_processed 
- Child 4: Andrés, 2010, 0 -> not_modified 
- Child 5: , ,  -> not_processed 

...

SUMMARY
Families:
- 0 created. 
- 0 updated. 
- 2 not modified. 
- 0 errors. 
Parents:
- 0 created. 
- 0 updated. 
- 5 not modified. 
- 0 assigned to a family. 
- 0 errors. 
Children:
- 0 created. 
- 0 updated. 
- 5 not modified. 
- 0 errors. 
Bank accounts:
- 0 created. 
- 0 updated. 
- 3 not modified. 
- 0 family default bank accounts changed. 
- 0 errors. 
Errors:
- No errors

```