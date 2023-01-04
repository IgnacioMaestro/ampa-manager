import traceback

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.management.commands.results.import_member_result import ImportMemberResult


class BankAccountImporter:

    def __init__(self, sheet, columns_indexes):
        self.sheet = sheet
        self.columns_indexes = columns_indexes

    def import_bank_account(self, row_index, parent_number, parent, family):
        bank_account = None
        result = ImportMemberResult(BankAccount.__name__, row_index)

        try:
            fields = self.import_fields(row_index, parent_number)
            result.fields_excel = fields.get_list()

            if fields.iban and parent:
                bank_account = parent.find_bank_account(fields.iban)
                if bank_account:
                    if BankAccountImporter.is_modified(bank_account, parent):
                        fields_before, fields_after = BankAccountImporter.update(bank_account, parent)
                        result.set_updated(fields_before, fields_after)
                    else:
                        result.set_not_modified()
                else:
                    bank_account = BankAccount.objects.create(swift_bic=fields.swift_bic, iban=fields.iban, owner=parent)
                    result.set_created()

                if family and not parent.belong_to_family(family):
                    family.parents.add(parent)
                    result.set_added_to_family()

                if fields.is_default_account and family and family.default_bank_account != bank_account:
                    family.default_bank_account = bank_account
                    family.save()
                    result.set_as_default()
            else:
                result.set_not_processed()

        except Exception as e:
            print(traceback.format_exc())
            result.set_error(f'Exception: {e}')

        return bank_account, result

    def import_fields(self, row_index, parent_number):
        swift_bic = None
        iban = None
        is_default_account = None

        if parent_number in [1, 2]:
            swift_bic_index = None
            iban_index = None
            is_default_account_index = None

            if parent_number == 1:
                swift_bic_index = self.columns_indexes['parent1_swift_bic']
                iban_index = self.columns_indexes['parent1_iban']
                is_default_account_index = self.columns_indexes['parent1_is_default']
            elif parent_number == 2:
                swift_bic_index = self.columns_indexes['parent2_swift_bic']
                iban_index = self.columns_indexes['parent2_iban']
                is_default_account_index = self.columns_indexes['parent2_is_default']

            swift_bic = FieldsFormatters.clean_iban(self.sheet.cell_value(rowx=row_index, colx=swift_bic_index))
            iban = FieldsFormatters.clean_string(self.sheet.cell_value(rowx=row_index, colx=iban_index))
            is_default_account = FieldsFormatters.parse_bool(self.sheet.cell_value(rowx=row_index, colx=is_default_account_index))

        return BankAccountImportedFields(swift_bic, iban, is_default_account)

    @staticmethod
    def is_modified(bank_account, parent):
        return bank_account.owner != parent

    @staticmethod
    def update(bank_account, parent):
        fields_before = [bank_account.swift_bic, bank_account.iban, bank_account.owner]
        bank_account.owner = parent
        bank_account.save()
        fields_after = [bank_account.swift_bic, bank_account.iban, bank_account.owner]
        return fields_before, fields_after
