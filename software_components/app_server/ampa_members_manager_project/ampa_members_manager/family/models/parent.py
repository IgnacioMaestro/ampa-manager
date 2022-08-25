from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Parent(models.Model):
    name_and_surnames = models.CharField(max_length=500, verbose_name=_("Name and surnames"), unique=True)
    phone_number = PhoneNumberField(verbose_name=_("Phone number"))
    additional_phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("Additional phone number"))

    class Meta:
        verbose_name = _('Parent')
        verbose_name_plural = _("Parents")

    @property
    def full_name(self) -> str:
        return str(self.name_and_surnames)

    def __str__(self) -> str:
        return self.full_name
