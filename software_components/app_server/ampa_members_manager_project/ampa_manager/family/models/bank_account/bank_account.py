from django.core.exceptions import ValidationError
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from localflavor.generic.models import IBANField, BICField
from localflavor.generic.validators import IBANValidator

from ampa_manager.family.models.bank_account.bank_account_queryset import BankAccountQuerySet
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.utils.fields_formatters import FieldsFormatters


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

    @property
    def bank_code(self):
        if str(self.iban):
            if len(str(self.iban)) == 24:
                return str(self.iban)[4:8]
            elif len(str(self.iban)) == 20:
                return str(self.iban)[0:4]
        return None

    def complete_swift_bic(self):
        self.swift_bic = BankBicCode.get_bic_code(self.bank_code)

    def save(self, *args, **kwargs):
        if self.swift_bic in [None, '']:
            self.complete_swift_bic()
        super(BankAccount, self).save(**kwargs)

    def clean_iban(self):
        cleaned_iban = FieldsFormatters.clean_iban(self.cleaned_data['iban'])
        if not BankAccount.iban_is_valid(cleaned_iban):
            raise ValidationError(_('The IBAN code is not valid'))
        return cleaned_iban

    @staticmethod
    def iban_is_valid(iban: str) -> bool:
        try:
            validator = IBANValidator()
            validator(iban)
        except ValidationError:
            return False
        return True
