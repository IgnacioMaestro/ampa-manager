import traceback
import xlrd

from django.core.management.base import BaseCommand

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.models.child import Child
from ampa_manager.management.commands.utils.logger import Logger
from ampa_manager.management.commands.utils.family_importer import FamilyImporter
from ampa_manager.management.commands.utils.parent_importer import ParentImporter
from ampa_manager.management.commands.utils.child_importer import ChildImporter
from ampa_manager.management.commands.utils.bank_account_importer import BankAccountImporter


class Command(BaseCommand):
    help = 'Import families, parents, children and bank accounts from an excel file'

    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 3

    FAMILY_SURNAMES_INDEX = 0

    PARENT1_FULL_NAME_INDEX = 1
    PARENT1_PHONE1_INDEX = 2
    PARENT1_PHONE2_INDEX = 3
    PARENT1_EMAIL_INDEX = 4
    PARENT1_SWIFT_BIC_INDEX = 5
    PARENT1_IBAN_INDEX = 6
    PARENT1_IS_DEFAULT_INDEX = 7

    PARENT2_FULL_NAME_INDEX = 8
    PARENT2_PHONE1_INDEX = 9
    PARENT2_PHONE2_INDEX = 10
    PARENT2_EMAIL_INDEX = 11
    PARENT2_SWIFT_BIC_INDEX = 12
    PARENT2_IBAN_INDEX = 13
    PARENT2_IS_DEFAULT_INDEX = 14

    CHILD1_NAME_INDEX = 15
    CHILD1_YEAR_INDEX = 16
    CHILD1_LEVEL_INDEX = 17

    CHILD2_NAME_INDEX = 18
    CHILD2_YEAR_INDEX = 19
    CHILD2_LEVEL_INDEX = 20

    CHILD3_NAME_INDEX = 21
    CHILD3_YEAR_INDEX = 22
    CHILD3_LEVEL_INDEX = 23

    CHILD4_NAME_INDEX = 24
    CHILD4_YEAR_INDEX = 25
    CHILD4_LEVEL_INDEX = 26

    CHILD5_NAME_INDEX = 27
    CHILD5_YEAR_INDEX = 28
    CHILD5_LEVEL_INDEX = 29

    results = []
    totals = {}

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            self.logger = Logger()
            self.load_excel(options['file'])

            self.family_importer = FamilyImporter(self.sheet, Command.FAMILY_SURNAMES_INDEX,
                                                  Command.PARENT1_FULL_NAME_INDEX, Command.PARENT2_FULL_NAME_INDEX)
            self.parent_importer = ParentImporter(self.sheet, Command.PARENT1_FULL_NAME_INDEX,
                                                  Command.PARENT1_PHONE1_INDEX, Command.PARENT1_PHONE2_INDEX,
                                                  Command.PARENT1_EMAIL_INDEX, Command.PARENT2_FULL_NAME_INDEX,
                                                  Command.PARENT2_PHONE1_INDEX, Command.PARENT2_PHONE2_INDEX,
                                                  Command.PARENT2_EMAIL_INDEX)
            self.child_importer = ChildImporter(self.sheet, xls_settings)
            self.bank_account_importer = BankAccountImporter(self.sheet, xls_settings)

            self.set_totals_before()

            for row_index in range(xls_settings.FIRST_ROW_INDEX, self.sheet.nrows):
                row_number = row_index + 1
                self.logger.log(f'\nRow {row_number}')

                family, result = self.family_importer.import_family(row_index)
                self.process_result(result)

                parent1, result = self.parent_importer.import_parent(row_index, 1, family)
                self.process_result(result)

                parent2, result = self.parent_importer.import_parent(row_index, 2, family)
                self.process_result(result)

                _, result = self.bank_account_importer.import_bank_account(row_index, 1, parent1, family)
                self.process_result(result)

                _, result = self.bank_account_importer.import_bank_account(row_index, 2, parent2, family)
                self.process_result(result)

                _, result = self.child_importer.import_child(row_index, 1, family)
                self.process_result(result)

                _, result = self.child_importer.import_child(row_index, 2, family)
                self.process_result(result)

                _, result = self.child_importer.import_child(row_index, 3, family)
                self.process_result(result)

                _, result = self.child_importer.import_child(row_index, 4, family)
                self.process_result(result)

                _, result = self.child_importer.import_child(row_index, 5, family)
                self.process_result(result)

            self.set_totals_after()
            
            self.print_stats()
        except:
            print(traceback.format_exc())
        finally:
            self.logger.close_file()
    
    def load_excel(self, file_path):
        self.logger.log(f'\nImporting file {file_path}')
        self.book = xlrd.open_workbook(file_path)
        self.sheet = self.book.sheet_by_index(xls_settings.SHEET_NUMBER)
    
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

    def print_stats(self):
        self.logger.log('\nSUMMARY\n')

        rows_with_data_count = self.sheet.nrows - xls_settings.FIRST_ROW_INDEX
        self.logger.log(f' - Rows with data: {rows_with_data_count} (rows {xls_settings.FIRST_ROW_INDEX+1} to {self.sheet.nrows}). Sheet: "{self.sheet.name}"')

        self.totals = self.totalize_results()
        for class_name, states in self.totals.items():
            variation = self.get_totals_variation(class_name)
            self.logger.log(f' - {class_name} ({variation}):')

            for state, total in states.items():
                self.logger.log(f'   - {state.name}: {total}:')

        self.logger.log(f'\nVALIDATIONS:\n')

        parents_without_family = Parent.objects.has_no_family().count()
        self.logger.log(f'- Parents without family: {parents_without_family}')

        parents_in_multiple_families = Parent.objects.has_multiple_families().count()
        self.logger.log(f'- Parents with multiple families: {parents_in_multiple_families}')

        parents_with_multiple_bank_accounts = Parent.objects.with_multiple_bank_accounts().count()
        self.logger.log(f'- Parents with multiple bank accounts: {parents_with_multiple_bank_accounts}')

        families_without_account = Family.objects.without_default_bank_account().count()
        self.logger.log(f'- Families without bank account: {families_without_account}')

        families_with_more_than_2_parents = Family.objects.with_more_than_two_parents().count()
        self.logger.log(f'- Families with more than 2 parents: {families_with_more_than_2_parents}')

        errors = self.get_errors()
        self.logger.log(f'\nERRORS ({len(errors)}):\n')
        if len(errors) > 0:
            for error in errors:
                self.logger.error(f'- {error} ')
        else:
            self.logger.log(f'- No errors\n')
    
    def get_errors(self):
        errors = []
        for result in self.results:
            if result.error:
                message = f'Row {result.row_index+1}: {result.error}'
                errors.append(message)
        return errors

    def process_result(self, result):
        self.logger.log_result(result)
        self.results.append(result)

    def set_totals_before(self):
        self.totals_before = {}

        self.totals_before[Family.__name__] = Family.objects.count()
        self.totals_before[Parent.__name__] = Parent.objects.count()
        self.totals_before[Child.__name__] = Child.objects.count()
        self.totals_before[BankAccount.__name__] = BankAccount.objects.count()

    def set_totals_after(self):
        self.totals_after = {}

        self.totals_after[Family.__name__] = Family.objects.count()
        self.totals_after[Parent.__name__] = Parent.objects.count()
        self.totals_after[Child.__name__] = Child.objects.count()
        self.totals_after[BankAccount.__name__] = BankAccount.objects.count()

    def get_totals_variation(self, class_name):
        return f'{self.totals_before[class_name]} -> {self.totals_after[class_name]}'
