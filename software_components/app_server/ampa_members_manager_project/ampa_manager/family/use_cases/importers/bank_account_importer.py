from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.iban import IBAN
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult


class BankAccountImporter:

    @staticmethod
    def find(iban):
        try:
            return BankAccount.objects.get(iban=iban)
        except BankAccount.DoesNotExist:
            return None

    @staticmethod
    def import_bank_account(parent, iban) -> ImportModelResult:
        result = ImportModelResult(BankAccount.__name__, [iban])

        if parent:
            if iban:
                bank_account = BankAccountImporter.find(iban)
                if bank_account:
                    if bank_account.owner == parent:
                        result.set_not_modified(bank_account)
                    else:
                        result.set_error(f'Owner does not match. Current owner: {bank_account.owner}. New: {parent}')
                elif IBAN.is_valid(iban):
                    bank_account = BankAccount.objects.create(iban=iban, owner=parent)
                    result.set_created(bank_account)
                else:
                    result.set_error('IBAN not valid')
            else:
                result.set_error('Missing IBAN')
        else:
            result.set_error('Missing owner')

        return result