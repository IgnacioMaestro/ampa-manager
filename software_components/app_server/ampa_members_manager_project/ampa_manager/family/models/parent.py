import re

from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from ampa_manager.family.models.parent_queryset import ParentQuerySet
from ampa_manager.management.commands.import_command.importer import Importer


class Parent(TimeStampedModel):
    name_and_surnames = models.CharField(max_length=500, verbose_name=_("Name and surnames"), unique=True)
    phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("Phone number"))
    additional_phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("Other phone"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Email"))

    objects = Manager.from_queryset(ParentQuerySet)()

    class Meta:
        verbose_name = _('Parent')
        verbose_name_plural = _("Parents")
        db_table = 'parent'

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return str(self.name_and_surnames)

    def belong_to_family(self, family):
        return self.family_set.filter(surnames=family.surnames).exists()
    
    def clean_name_and_surnames(self):
        return Importer.clean_surname(self.cleaned_data['name_and_surnames'])

    def match(self, name_and_surnames):
        if name_and_surnames and self.name_and_surnames:
            if name_and_surnames in self.name_and_surnames or self.name_and_surnames in name_and_surnames:
                return True
            for word in self.name_and_surnames.strip().split(' '):
                pattern = rf'\b{word}\b'
                if re.search(pattern, name_and_surnames, re.IGNORECASE):
                    return True
        return False

    @staticmethod
    def find(family, name_and_surnames):
        if name_and_surnames:
            parents = Parent.objects.with_full_name(name_and_surnames)
            if parents.count() == 1:
                return parents.first()
            else:
                for parent in family.parents.all():
                    if parent.match(name_and_surnames):
                        return parent
        return None

    @staticmethod
    def fix_name_and_surnames():
        for parent in Parent.objects.all():
            fixed_name_and_surnames = Importer.clean_surname(parent.name_and_surnames)
            if fixed_name_and_surnames != parent.name_and_surnames:
                print(f'Parent name and surnames fixed: "{parent.name_and_surnames}" -> "{fixed_name_and_surnames}"')
                parent.name_and_surnames = fixed_name_and_surnames
                parent.save(update_fields=['name_and_surnames'])
