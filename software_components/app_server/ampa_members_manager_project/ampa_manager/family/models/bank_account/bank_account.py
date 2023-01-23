from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from localflavor.generic.models import IBANField, BICField

from ampa_manager.family.models.bank_account.bank_account_queryset import BankAccountQuerySet
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.models.bank_account.iban import IBAN
from ampa_manager.utils.fields_formatters import FieldsFormatters


class BankAccount(TimeStampedModel):
    swift_bic = BICField(verbose_name=_("SWIFT/BIC"), null=True, blank=True)
    iban = IBANField(unique=True, verbose_name=_("IBAN"))
    owner = models.ForeignKey(to=Parent, on_delete=CASCADE, verbose_name=_("Owner"))

    objects = Manager.from_queryset(BankAccountQuerySet)()

    class Meta:
        verbose_name = _('Bank account')
        verbose_name_plural = _('Bank accounts')
        db_table = 'bank_account'
        ordering = ['owner__name_and_surnames', 'iban']

    def __str__(self) -> str:
        return f'{self.owner} {self.iban}'

    def complete_swift_bic(self):
        self.swift_bic = BankBicCode.get_bic_code(self.bank_code)

    @property
    def bank_code(self):
        iban_value = str(self.iban)
        if iban_value:
            if len(iban_value) == 24:
                return self.iban[4:8]
            elif len(iban_value) == 20:
                return self.iban[0:4]
        return None

    @staticmethod
    def get_csv_fields(bank_accounts):
        csv_fields = []
        for bank_account in bank_accounts:
            csv_fields.append([str(bank_account.owner), bank_account.iban])
        return csv_fields

    def save(self, *args, **kwargs):
        if self.swift_bic in [None, '']:
            self.complete_swift_bic()
        super(BankAccount, self).save(**kwargs)

    def clean_iban(self):
        if not IBAN.is_valid(FieldsFormatters.clean_iban(self.cleaned_data['iban'])):
            raise ValidationError(_('The IBAN code is not valid'))
