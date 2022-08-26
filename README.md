# AMPAMembersManager

## Domain model diagram
[Domain model diagram](doc/DomainModelDiagram/DomainModelDiagram.md)

## Use cases diagram
[Use cases diagram](doc/Use%20cases%20diagram.md)

## Translations
1. Generate translations files

``
django-admin makemessages -l es -l eu
``

2. Edit translations files. 
   1. Check translations marked as "fuzzy" (translated automatically by django based on similar translations)
   2. Empty translations: look for ``msgstr ""``

```
locale/es/LC_MESSAGES/django.po 
locale/eu/LC_MESSAGES/django.po
```

3. Compile translations files

``
django-admin compilemessages
``

## Import from excel

``
python manage.py import <FILE_PATH>
``