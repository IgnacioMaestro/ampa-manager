from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class ParentImportData(models.Model):
    name_and_surnames = models.CharField(max_length=500, verbose_name=_("Name and surnames"), unique=True)
    phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("Phone number"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Email"))

    class Meta:
        abstract = True
        verbose_name = _('Parent import data')
        verbose_name_plural = _('Parent import data')

