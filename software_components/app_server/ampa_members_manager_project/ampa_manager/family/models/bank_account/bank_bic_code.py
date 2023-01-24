from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _


class BankBicCode(models.Model):
    bank_code = models.CharField(unique=True, max_length=4, verbose_name=_("Bank code"), help_text=_('4 characters'))
    bic_code = models.CharField(unique=True, max_length=11, verbose_name=_("BIC code"), help_text=_('8-11 characters: Entity (4), Country (2), City (2), Office (3, Optional)'))

    def __str__(self) -> str:
        return f'{self.bic_code} {self.bank_code}'

    @staticmethod
    def get_bic_code(bank_code: str) -> Optional[str]:
        try:
            bank_bic = BankBicCode.objects.get(bank_code=bank_code)
            return bank_bic.bic_code
        except BankBicCode.DoesNotExist:
            return None
