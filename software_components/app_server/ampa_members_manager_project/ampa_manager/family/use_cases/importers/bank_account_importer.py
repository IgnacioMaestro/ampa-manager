from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.parent import Parent


class BankAccountImporter:

    def __init__(self, parent: Parent, iban: str):
        self.result = ImportModelResult(BankAccount.__name__)
        self.parent = parent
        self.iban = iban
        self.bank_account = None

    def import_bank_account(self) -> ImportModelResult:
        if self.iban:
            self.bank_account = BankAccount.find(self.iban)
            if self.bank_account:
                self.result.set_not_modified(self.bank_account)
            elif BankAccount.iban_is_valid(self.iban):
                self.bank_account = BankAccount.objects.create(iban=self.iban)
                self.result.set_created(self.bank_account)
            else:
                self.result.set_error(_('IBAN not valid'))
        else:
            self.result.set_error(_('Missing IBAN'))

        return self.result
