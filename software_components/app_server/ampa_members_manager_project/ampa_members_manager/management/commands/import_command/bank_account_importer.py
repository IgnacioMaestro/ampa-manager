import traceback

from ampa_members_manager.management.commands.import_command.importer import Importer
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.management.commands.import_command.processing_result import ProcessingResult


class BankAccountImporter(Importer):

    def __init__(self, sheet, xls_settings):
        self.sheet = sheet
        self.xls_settings = xls_settings
    
    def get_fields(self, row_index, parent_number):
        if parent_number in [1, 2]:
            if parent_number == 1:
                swift_bic_index = self.xls_settings.PARENT1_SWIFT_BIC_INDEX
                iban_index = self.xls_settings.PARENT1_IBAN_INDEX
                is_default_account_index = self.xls_settings.PARENT1_IS_DEFAULT_INDEX
            elif parent_number == 2:
                swift_bic_index = self.xls_settings.PARENT2_SWIFT_BIC_INDEX
                iban_index = self.xls_settings.PARENT2_IBAN_INDEX
                is_default_account_index = self.xls_settings.PARENT2_IS_DEFAULT_INDEX
            
            swift_bic = Importer.clean_iban(self.sheet.cell_value(rowx=row_index, colx=swift_bic_index))
            iban = Importer.clean_string_value(self.sheet.cell_value(rowx=row_index, colx=iban_index))
            is_default_account = Importer.parse_bool(self.sheet.cell_value(rowx=row_index, colx=is_default_account_index))

            return swift_bic, iban, is_default_account
        return None, None, None

    def import_bank_account(self, row_index, parent_number, parent, family):
        bank_account = None
        result = ProcessingResult(BankAccount.__name__, row_index)

        try:
            swift_bic, iban, is_default_account = self.get_fields(row_index, parent_number)
            result.fields_excel = [swift_bic, iban, is_default_account]

            if iban and parent:
                bank_accounts = BankAccount.objects.with_iban(iban=iban)
                if bank_accounts.count() == 1:
                    bank_account = bank_accounts[0]
                    if bank_account.swift_bic != swift_bic or bank_account.owner != parent:
                        fields_before = [bank_account.swift_bic, bank_account.iban, bank_account.owner]
                        bank_account.swift_bic = swift_bic
                        bank_account.owner = parent
                        bank_account.save()
                        fields_after = [bank_account.swift_bic, bank_account.iban, bank_account.owner]
                        result.set_updated(fields_before, fields_after)
                    else:
                        result.set_not_modified()
                elif bank_accounts.count() > 1:
                    result.set_error('There is more than one bank account with iban "{iban}"')
                else:
                    bank_account = BankAccount.objects.create(swift_bic=swift_bic, iban=iban, owner=parent)
                    result.set_created()
            else:
                result.set_not_processed()

            if is_default_account and family and family.default_bank_account != bank_account:
                family.default_bank_account = bank_account
                family.save()
                result.set_as_default()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return bank_account, result