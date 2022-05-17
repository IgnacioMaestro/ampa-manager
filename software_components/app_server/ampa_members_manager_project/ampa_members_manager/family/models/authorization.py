from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext as _

from ampa_members_manager.family.models.bank_account import BankAccount


class Authorization(models.Model):
    number = models.CharField(verbose_name=_("Number"), max_length=50)
    date = models.DateField(verbose_name=_("Date"))
    bank_account = models.OneToOneField(verbose_name=_("Bank account"), to=BankAccount, on_delete=CASCADE)

    class Meta:
        verbose_name = _('Authorization')
        verbose_name_plural = _('Authorizations')

    def __str__(self) -> str:
        return f'{self.number}-{str(self.bank_account)}'