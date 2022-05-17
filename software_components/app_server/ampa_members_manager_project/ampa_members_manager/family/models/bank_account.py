from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext as _
from localflavor.generic.models import IBANField, BICField

from ampa_members_manager.family.models.parent import Parent


class BankAccount(models.Model):
    swift_bic = BICField(verbose_name=_("SWIFT/BIC"))
    iban = IBANField(verbose_name=_("IBAN"), unique=True)
    owner = models.ForeignKey(verbose_name=_("Owner"), to=Parent, on_delete=CASCADE)

    class Meta:
        verbose_name = _('Bank account')
        verbose_name_plural = _('Bank accounts')

    def __str__(self) -> str:
        return f'{self.iban} {self.owner}'
