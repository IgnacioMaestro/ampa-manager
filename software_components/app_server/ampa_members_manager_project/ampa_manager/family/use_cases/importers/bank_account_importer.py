from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.management.commands.results.model_import_result import ModelImportResult


class BankAccountImporter:

    @staticmethod
    def find(iban):
        try:
            return BankAccount.objects.get(iban=iban)
        except BankAccount.DoesNotExist:
            return None

    @staticmethod
    def import_bank_account(parent, iban, swift_bic, is_default_account=False, family=None) -> ModelImportResult:
        result = ModelImportResult(BankAccount.__name__)

        if parent:
            if iban:
                bank_account = BankAccountImporter.find(iban)
                if bank_account:
                    if bank_account.owner == parent:
                        if bank_account.swift_bic != swift_bic:
                            fields_before = [bank_account.swift_bic]
                            bank_account.swift_bic = swift_bic
                            fields_after = [swift_bic]
                            bank_account.save()
                            result.set_updated(bank_account, fields_before, fields_after)
                        else:
                            result.set_not_modified(bank_account)

                        if is_default_account and family and family.default_bank_account != bank_account:
                            family.default_bank_account = bank_account
                            family.save()
                            result.set_as_default()
                    else:
                        result.set_error(f'Owner does not match. Current owner: {bank_account.owner}. New: {parent}')
                else:
                    bank_account = BankAccount.objects.create(iban=iban, owner=parent)
                    result.set_created(bank_account)
            else:
                result.set_error('Missing IBAN')
        else:
            result.set_error('Missing owner')

        return result