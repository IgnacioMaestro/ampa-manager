# AMPA Manager

## Diagrama del modelo del dominio
[Domain model diagram](doc/DomainModelDiagram/DomainModelDiagram.md)

## Diagramas de casos de uso
[Use cases diagram](doc/UseCasesDiagram/Use%20cases%20diagram.md)

## Configurar base de datos

1. Descargar fichero db.sqlite3 del drive (Ordenadores > PC AMPA > database)
1. Reemplazar ampa_members_manager_project\database\db.sqlite3
1. Realizar modificaciones
1. Subir el fichero al drive (Ordenadores > PC AMPA > database)

## Traducciones

1. Generar ficheros de traducciones

```
django-admin makemessages -l es -l eu
```

2. Completar las traducciones
   1. Buscar traducciones marcadas como "fuzzy" (son traducciones automáticas basadas en textos similares)
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
