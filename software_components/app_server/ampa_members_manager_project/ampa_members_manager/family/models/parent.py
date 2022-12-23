from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Manager
from django_extensions.db.models import TimeStampedModel

from phonenumber_field.modelfields import PhoneNumberField
from ampa_members_manager.family.models.parent_queryset import ParentQuerySet


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
