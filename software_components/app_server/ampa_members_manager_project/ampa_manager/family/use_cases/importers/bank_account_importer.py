from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.bank_account.iban import IBAN
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult


class BankAccountImporter:

    @staticmethod
    def find(iban):
        try:
            return BankAccount.objects.get(iban=iban)
        except BankAccount.DoesNotExist:
            return None

    @staticmethod
    def import_bank_account_and_holder(parent, iban) -> (ImportModelResult, ImportModelResult):
        bank_account_result = BankAccountImporter.import_bank_account(iban)
        bank_account = bank_account_result.imported_object

        holder_result = BankAccountImporter.import_holder(parent, bank_account)
        return bank_account_result, holder_result

    @staticmethod
    def import_bank_account(iban) -> ImportModelResult:
        result = ImportModelResult(BankAccount.__name__, [iban])

        if iban:
            bank_account = BankAccountImporter.find(iban)
            if bank_account:
                result.set_not_modified(bank_account)
            elif IBAN.is_valid(iban):
                bank_account = BankAccount.objects.create(iban=iban)
                result.set_created(bank_account)
            else:
                result.set_error('IBAN not valid')
        else:
            result.set_error('Missing IBAN')

        return result

    @staticmethod
    def import_holder(parent: Parent, bank_account: BankAccount) -> ImportModelResult:
        result = ImportModelResult(Holder.__name__, [])

        if parent:
            if bank_account:
                holder = Holder.find(parent, bank_account)
                if holder:
                    result.set_not_modified(holder)
                else:
                    holder = Holder.objects.create_for_active_course(parent=parent, bank_account=bank_account)
                    result.set_created(holder)
            else:
                result.set_error('Missing bank account')
        else:
            result.set_error('Missing owner')

        return result
