import traceback

from django.core.management.base import BaseCommand

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.importers.member_excel_importer import MemberImportResult, MemberExcelImporter, \
    MemberExcelRowFields
from ampa_manager.management.commands.utils.logger import Logger


class Command(BaseCommand):
    help = 'Import families, parents, children and bank accounts from an excel file'

    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 3

    results = []
    totals = {}

    def __init__(self):
        super().__init__()
        self.logger = Logger('import_registrations')

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            excel_file_name = options['file']
            excel_importer = MemberExcelImporter(excel_file_name, Command.SHEET_NUMBER, Command.FIRST_ROW_INDEX)

            results = []
            counters_before = Command.count_objects()
            for member_fields in excel_importer.import_rows():
                result = self.import_member(member_fields)
                result.print(self.logger)
                results.append(result)

            counters_after = Command.count_objects()
            MemberImportResult.print_stats(self.logger, results, counters_before, counters_after)

        except:
            self.logger.error(traceback.format_exc())
        finally:
            if self.logger:
                self.logger.close_log_file()

    def totalize_results(self):
        totals = {}
        for result in self.results:
            if result.class_name not in totals:
                totals[result.class_name] = {}

            for state in [result.state, result.state2]:
                if state:
                    if state not in totals[result.class_name]:
                        totals[result.class_name][state] = 1
                    else:
                        totals[result.class_name][state] += 1
        return totals
    
    def get_total(self, state, class_name):
        return self.totals.get(class_name, {}).get(state, 0)

    def get_errors(self):
        errors = []
        for result in self.results:
            if result.error:
                message = f'Row {result.row_index+1}: {result.error}'
                errors.append(message)
        return errors

    @staticmethod
    def count_objects():
        return {
            'families': Family.objects.count(),
            'parents': Parent.objects.count(),
            'children': Child.objects.count(),
            'bank_accounts': BankAccount.objects.count(),
        }

    def import_member(self, fields: MemberExcelRowFields):
        result = MemberImportResult(fields.row_index)

        try:
            family, result.family_state, error = Family.import_family(fields.family_surnames,
                                                                      fields.parent1_name_and_surnames,
                                                                      fields.parent2_name_and_surnames)
            if not family:
                result.add_error(error)
                return result

            child1, result.child1_state, error = Child.import_child(family, fields.child1_name,
                                                                    fields.child1_level,
                                                                    fields.child1_year_of_birth)
            if fields.child1_has_data() and not child1:
                result.add_error(error)
                return result

            child2, result.child2_state, error = Child.import_child(family, fields.child2_name,
                                                                    fields.child2_level,
                                                                    fields.child2_year_of_birth)
            if fields.child2_has_data() and not child2:
                result.add_error(error)
                return result

            child3, result.child3_state, error = Child.import_child(family, fields.child3_name,
                                                                    fields.child3_level,
                                                                    fields.child3_year_of_birth)
            if fields.child3_has_data() and not child3:
                result.add_error(error)
                return result

            child4, result.child4_state, error = Child.import_child(family, fields.child4_name,
                                                                    fields.child4_level,
                                                                    fields.child4_year_of_birth)
            if fields.child4_has_data() and not child4:
                result.add_error(error)
                return result

            child5, result.child5_state, error = Child.import_child(family, fields.child5_name,
                                                                    fields.child5_level,
                                                                    fields.child5_year_of_birth)
            if fields.child5_has_data() and not child5:
                result.add_error(error)
                return result

            parent1, result.parent1_state, error = Parent.import_parent(family,
                                                                        fields.parent1_name_and_surnames,
                                                                        fields.parent1_phone_number,
                                                                        fields.parent1_additional_phone_number,
                                                                        fields.parent1_email)
            if fields.parent1_has_data() and not parent1:
                result.add_error(error)
                return result

            parent2, result.parent2_state, error = Parent.import_parent(family,
                                                                        fields.parent2_name_and_surnames,
                                                                        fields.parent2_phone_number,
                                                                        fields.parent2_additional_phone_number,
                                                                        fields.parent2_email)
            if fields.parent2_has_data() and not parent2:
                result.add_error(error)
                return result

            bank_account1, result.bank_account1_state, error = BankAccount.import_bank_account(parent1,
                                                                                               fields.parent1_bank_account_iban,
                                                                                               fields.parent1_bank_account_swift_bic)
            if fields.parent1_bank_account_has_data() and not bank_account1:
                result.add_error(error)
                return result

            bank_account2, result.bank_account2_state, error = BankAccount.import_bank_account(parent2,
                                                                                               fields.parent2_bank_account_iban,
                                                                                               fields.parent2_bank_account_swift_bic)
            if fields.parent2_bank_account_has_data() and not bank_account2:
                result.add_error(error)
                return result

        except Exception as e:
            self.logger.error(f'Row {fields.row_index + 1}: {traceback.format_exc()}')
            result.add_error(str(e))

        return result
