from django.core.exceptions import ValidationError
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from localflavor.generic.models import IBANField, BICField

from ampa_manager.family.models.bank_account.bank_account_queryset import BankAccountQuerySet
from ampa_manager.family.models.bank_account.bic_code import BicCode
from ampa_manager.family.models.bank_account.iban import IBAN


class BankAccount(TimeStampedModel):
    swift_bic = BICField(verbose_name=_("SWIFT/BIC"), null=True, blank=True)
    iban = IBANField(unique=True, verbose_name=_("IBAN"))

    objects = Manager.from_queryset(BankAccountQuerySet)()

    class Meta:
        verbose_name = _('Bank account')
        verbose_name_plural = _('Bank accounts')
        db_table = 'bank_account'
        ordering = ['iban']

    def __str__(self) -> str:
        return f'{self.iban}'

    def complete_swift_bic(self):
        self.swift_bic = BicCode.get_bic_code(self.iban)

    def save(self, *args, **kwargs):
        if self.swift_bic in [None, '']:
            self.complete_swift_bic()
        super(BankAccount, self).save(**kwargs)

    def clean_iban(self):
        if not IBAN.is_valid(self.cleaned_data['iban']):
            raise ValidationError(_('The IBAN code is not valid'))
