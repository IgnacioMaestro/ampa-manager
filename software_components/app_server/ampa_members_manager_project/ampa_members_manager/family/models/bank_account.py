from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _
from localflavor.generic.models import IBANField, BICField

from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.bic_code import BicCode


class BankAccount(models.Model):
    swift_bic = BICField(verbose_name=_("SWIFT/BIC"), null=True, blank=True)
    iban = IBANField(unique=True, verbose_name=_("IBAN"))
    owner = models.ForeignKey(to=Parent, on_delete=CASCADE, verbose_name=_("Owner"))

    class Meta:
        verbose_name = _('Bank account')
        verbose_name_plural = _('Bank accounts')
        ordering = ['owner__name_and_surnames', 'iban']

    def __str__(self) -> str:
        return f'{self.owner} {self.iban}'
    
    def save(self, *args, **kwargs):
        if not self.swift_bic:
            self.swift_bic = BicCode.get_bic_code(self.iban)
        
        super(BankAccount, self).save(*args, **kwargs)
