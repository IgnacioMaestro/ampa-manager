from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Parent(models.Model):
    name = models.CharField(max_length=500, verbose_name=_("Name"))
    first_surname = models.CharField(max_length=500, verbose_name=_("First surname"))
    second_surname = models.CharField(max_length=500, verbose_name=_("Second surname"))
    phone_number = PhoneNumberField(verbose_name=_("Phone number"))
    additional_phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("Additional phone number"))

    class Meta:
        verbose_name = _('Parent')
        verbose_name_plural = _("Parents")
        constraints = [
            models.UniqueConstraint(fields=['name', 'first_surname', 'second_surname'], name='unique_parent')]

    @property
    def full_name(self) -> str:
        return f'{self.name} {self.first_surname} {self.second_surname}'

    def __str__(self) -> str:
        return self.full_name
