from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _


class BankBicCode(models.Model):
    bank_code = models.CharField(unique=True, max_length=4, verbose_name=_("Bank code"), help_text=_('4 characters'))
    bic_code = models.CharField(unique=True, max_length=11, verbose_name=_("BIC code"), help_text=_('8-11 characters: Entity (4), Country (2), City (2), Office (3, Optional)'))

    def __str__(self) -> str:
        return f'{self.bic_code} {self.bank_code}'

    CODES = {
        "2100": "CAIXESBBXXX",
        "3035": "CLPEES2MXXX",
        "0073": "OPENESMMXXX",
        "2095": "BASKES2BXXX",
        "3008": "BCOEESMM008",
        "0081": "BSABESBBXXX",
        "0239": "EVOBESMMXXX",
        "0128": "BKBKESMMXXX",
        "2085": "CAZRES2ZXXX",
        "0138": "BKOAES22XXX",
        "0182": "BBVAESMMXXX",
        "0216": "CMCIESMMXXX",
        "0049": "BSCHESMMXXX",
        "1465": "INGDESMMXXX",
        "2080": "CAGLESMMXXX",
        "3076": "BCOEESMM076",
        "1491": "TRIOESMMXXX"
    }

    @staticmethod
    def get_bic_code(bank_code: str) -> Optional[str]:
        try:
            bank_bic = BankBicCode.objects.get(bank_code=bank_code)
            return bank_bic.bic_code
        except BankBicCode.DoesNotExist:
            return None
