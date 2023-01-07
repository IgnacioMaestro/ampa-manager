from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from localflavor.generic.models import IBANField, BICField

from ampa_manager.family.models.bank_account.bank_account_queryset import BankAccountQuerySet
from ampa_manager.family.bic_code import BicCode
from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.results.processing_state import ProcessingState


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
        self.swift_bic = BicCode.get_bic_code(self.iban)

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

    @staticmethod
    def find(iban):
        try:
            return BankAccount.objects.get(iban=iban)
        except BankAccount.DoesNotExist:
            return None

    @staticmethod
    def import_bank_account(parent, iban, swift_bic, is_default_account, family):
        bank_account = None
        error = None
        state_default_account = None

        if parent:
            if iban:
                bank_account = BankAccount.find(iban)
                if bank_account:
                    if bank_account.owner == parent:
                        if bank_account.swift_bic != swift_bic:
                            bank_account.swift_bic = swift_bic
                            bank_account.save()
                            state = ProcessingState.UPDATED
                        else:
                            state = ProcessingState.NOT_MODIFIED

                        if is_default_account and family.default_bank_account != bank_account:
                            family.default_bank_account = bank_account
                            family.save()
                            state_default_account = ProcessingState.BANK_ACCOUNT_SET_AS_DEFAULT
                    else:
                        state = ProcessingState.ERROR
                        error = f'Owner does not match. Current owner: {bank_account.owner}. New: {parent}'
                else:
                    bank_account = BankAccount.objects.create(iban=iban, owner=parent)
                    state = ProcessingState.CREATED
            else:
                state = ProcessingState.ERROR
                error = 'Missing IBAN'
        else:
            state = ProcessingState.ERROR
            error = 'Missing owner'

        return bank_account, state, state_default_account, error
