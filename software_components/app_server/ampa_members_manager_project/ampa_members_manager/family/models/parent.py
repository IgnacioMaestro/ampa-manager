from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext as _


class Parent(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=500)
    first_surname = models.CharField(verbose_name=_("First surname"), max_length=500)
    second_surname = models.CharField(verbose_name=_("Second surname"), max_length=500)
    phone_number = PhoneNumberField(verbose_name=_("Phone number"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'first_surname', 'second_surname'], name='unique_parent')]
        verbose_name = _('Parent')
        verbose_name_plural = _('Parents')

    @property
    def full_name(self) -> str:
        return f'{self.name} {self.first_surname} {self.second_surname}'

    def __str__(self) -> str:
        return self.full_name
