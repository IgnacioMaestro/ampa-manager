import re

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Manager
from django_extensions.db.models import TimeStampedModel

from phonenumber_field.modelfields import PhoneNumberField
from ampa_manager.family.models.parent_queryset import ParentQuerySet
from ampa_manager.management.commands.import_command.surnames import SURNAMES


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
    
    def clean(self):
        if self.name_and_surnames:
            self.name_and_surnames = self.name_and_surnames.title().strip()

    @staticmethod
    def find(family, name_and_surnames):
        if name_and_surnames:
            parents = Parent.objects.with_full_name(name_and_surnames)
            if parents.count() == 1:
                return parents.first()
            else:
                for parent in family.parents.all():
                    if name_and_surnames in parent.name_and_surnames or parent.name_and_surnames in name_and_surnames:
                        return parent
        return None

    @staticmethod
    def fix_accents():
        for parent in Parent.objects.all():
            for wrong, right in SURNAMES.items():
                pattern = rf'\b{wrong}\b'
                if re.search(pattern, parent.name_and_surnames):
                    before = parent.name_and_surnames
                    parent.name_and_surnames = re.sub(pattern, right, parent.name_and_surnames)
                    parent.save(update_fields=['name_and_surnames'])
                    print(f'Parent name and surnames fixed: {before} -> {parent.name_and_surnames}')
