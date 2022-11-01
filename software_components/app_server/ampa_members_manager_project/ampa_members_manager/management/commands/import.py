from datetime import datetime
import re
import xlrd
import traceback

from django.core.management.base import BaseCommand
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.academic_course.models.level import Level
from ampa_members_manager.management.commands.surnames import SURNAMES
from ampa_members_manager.management.commands.import_command.logger import Logger
from ampa_members_manager.management.commands.import_command.family_importer import FamilyImporter
from ampa_members_manager.management.commands.import_command.parent_importer import ParentImporter
from ampa_members_manager.management.commands.import_command.child_importer import ChildImporter
from ampa_members_manager.management.commands.import_command.bank_account_importer import BankAccountImporter

import ampa_members_manager.management.commands.members_excel_settings as xls_settings


class Command(BaseCommand):
    help = 'Import families, parents, childs and bank accounts from an excel file'

    STATUS_NOT_PROCESSED = 'not_processed'
    STATUS_CREATED = 'created'
    STATUS_UPDATED = 'updated'
    STATUS_UPDATED_ADDED_TO_FAMILY = 'added_to_family'
    STATUS_UPDATED_AS_DEFAULT = 'set_as_default'
    STATUS_NOT_MODIFIED = 'not_modified'
    STATUS_ERROR = 'error'
    TOTAL_BEFORE = 'before'
    TOTAL_AFTER = 'after'

    processed_objects = {}
    processing_errors = []
    totals = {}

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            self.logger = Logger()
            self.load_excel(options['file'])

            self.family_importer = FamilyImporter(self.sheet)
            self.parent_importer = ParentImporter(self.sheet)
            self.child_importer = ChildImporter(self.sheet)
            self.bank_account_importer = BankAccountImporter(self.sheet)
            
            self.import_file(options['file'])
            self.print_stats()
        except:
            self.logger.log(traceback.format_exc())
        finally:
            self.logger.close_file()
    
    def load_excel(self, file_path):
        self.logger.log(f'Importing file {file_path}')
        self.book = xlrd.open_workbook(file_path)
        self.sheet = self.book.sheet_by_index(xls_settings.SHEET_NUMBER)

    def import_file(self, file_path):
        self.logger.log(f'Importing file {file_path}')
        book = xlrd.open_workbook(file_path)
        sheet = book.sheet_by_index(xls_settings.SHEET_NUMBER)

        self.rows_count = sheet.nrows - xls_settings.FIRST_ROW_NUMBER
        self.logger.log(f'Importing {self.rows_count} rows (from row {xls_settings.FIRST_ROW_NUMBER+1} to row {sheet.nrows}). Sheet: "{sheet.name}". Rows: {sheet.nrows}')

        self.set_totals_before()

        for row_index in range(xls_settings.FIRST_ROW_NUMBER, sheet.nrows):
            row_number = row_index + 1
            self.logger.log(f'\nRow {row_number}')

            family = self.family_importer.import_family(row_index)
            parent1 = self.parent_importer.import_parent1(row_index)
            parent2 = self.parent_importer.import_parent2(row_index)

            self.bank_account_importer.import_parent1_bank_account(row_index)
            self.bank_account_importer.import_parent2_bank_account(row_index)

            self.bank_account_importer.import_parent1_bank_account(row_index)

            self.import_child1(sheet, family, row_index)
            self.import_child2(sheet, family, row_index)
            self.import_child3(sheet, family, row_index)
            self.import_child4(sheet, family, row_index)
            self.import_child5(sheet, family, row_index)
        
        self.set_totals_after()
    
    def print_stats(self):
        self.logger.log('')
        self.logger.log('SUMMARY')
        self.logger.log(f'Rows with data: {self.rows_count}')

        family_totals = self.get_totals(Family.__name__)
        self.logger.log(f'Families ({family_totals}):')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_CREATED, Family.__name__)} created. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_UPDATED, Family.__name__)} updated. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_NOT_MODIFIED, Family.__name__)} not modified. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_ERROR, Family.__name__)} errors. ')

        parent_totals = self.get_totals(Parent.__name__)
        self.logger.log(f'Parents ({parent_totals}):')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_CREATED, Parent.__name__)} created. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_UPDATED, Parent.__name__)} updated. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_NOT_MODIFIED, Parent.__name__)} not modified. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_UPDATED_ADDED_TO_FAMILY, Parent.__name__)} assigned to a family. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_ERROR, Parent.__name__)} errors. ')

        child_totals = self.get_totals(Child.__name__)
        self.logger.log(f'Children ({child_totals}):')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_CREATED, Child.__name__)} created. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_UPDATED, Child.__name__)} updated. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_NOT_MODIFIED, Child.__name__)} not modified. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_ERROR, Child.__name__)} errors. ')

        bank_account_totals = self.get_totals(BankAccount.__name__)
        self.logger.log(f'Bank accounts ({bank_account_totals}):')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_CREATED, BankAccount.__name__)} created. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_UPDATED, BankAccount.__name__)} updated. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_NOT_MODIFIED, BankAccount.__name__)} not modified. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_UPDATED_AS_DEFAULT, BankAccount.__name__)} set as family default. ')
        self.logger.log(f'- {self.get_status_total(Command.STATUS_ERROR, BankAccount.__name__)} errors. ')

        self.logger.log(f'Errors:')
        if len(self.processing_errors) > 0:
            for error in self.processing_errors:
                self.logger.error(f'- {error} ')
        else:
            self.logger.log(f'- No errors')

    def print_status(self, status, message):
        if status == Command.STATUS_ERROR:
            self.logger.error(message)
        elif status == Command.STATUS_NOT_PROCESSED:
            self.logger.warning(message)
        else:
            self.logger.log(message)

    def import_parent1_bank_account(self, sheet, parent, family, row_index):
        parent1_swift_bic = Command.clean_string_value(sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_SWIFT_BIC_INDEX))
        parent1_iban = Command.clean_string_value(sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_IBAN_INDEX))
        parent1_is_default_account = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_IS_DEFAULT_INDEX)

        self.import_bank_account(parent1_swift_bic, parent1_iban, parent1_is_default_account, parent, family, row_index, 1)

    def import_parent2_bank_account(self, sheet, parent, family, row_index):
        parent2_swift_bic = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_SWIFT_BIC_INDEX)
        parent2_iban = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_IBAN_INDEX)
        parent2_is_default_account = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_IS_DEFAULT_INDEX)

        self.import_bank_account(parent2_swift_bic, parent2_iban, parent2_is_default_account, parent, family, row_index, 2)
    
    @staticmethod
    def parse_bool(str_bool):
        if str_bool:
            return str_bool.strip().lower() in ["si", "sí", "yes", "1", "true"]
        else:
            return False
    
    @staticmethod
    def clean_email(str_value):
        return Command.clean_string_value(str_value, lower=True)
    
    @staticmethod
    def clean_surname(str_value):
        str_value = Command.clean_string_value(str_value, title=True)
        if str_value is not None:
            for wrong, right in SURNAMES.items():
                if wrong in str_value:
                    str_value = str_value.replace(wrong, right)
            return str_value
        return None

    @staticmethod
    def clean_string_value(str_value, lower=False, title=False):
        if str_value is not None:
            clean_value = Command.remove_duplicate_spaces(str_value).strip()
            if clean_value not in [' ', '']:
                if lower:
                    clean_value = clean_value.lower()
                if title:
                    clean_value = clean_value.title()
                return clean_value
        return None
    
    @staticmethod
    def remove_duplicate_spaces(str_value):
        if str_value is not None:
            return re.sub(' +', ' ', str(str_value))
        return None
    
    @staticmethod
    def clean_phone(phone):
        phone = Command.clean_string_value(phone)
        if phone and str(phone) not in ['0', '0.0', '0,0']:
            phone = str(phone)
            if not phone.startswith('+34'):
                phone = f'+34{phone}'
            if phone.endswith('.0'):
                phone = phone[:-2]
            if phone.endswith(',0'):
                phone = phone[:-2]
            return phone
        else:
            return ''

    def import_bank_account(self, swift_bic, iban, default_account, parent, family, row_index, parent_number):
        bank_account = None
        status = Command.STATUS_NOT_PROCESSED
        set_as_default = False
        error = ''

        try:
            swift_bic = swift_bic
            iban = iban
            default_account = Command.parse_bool(default_account)

            if iban and parent:
                bank_accounts = BankAccount.objects.by_iban(iban=iban)
                if bank_accounts.count() == 1:
                    bank_account = bank_accounts[0]
                    if bank_account.swift_bic != swift_bic or bank_account.owner != parent:
                        bank_account.swift_bic = swift_bic
                        bank_account.owner = parent
                        bank_account.save()
                        status = self.set_bank_account_status(Command.STATUS_UPDATED)
                    else:
                        status = self.set_bank_account_status(Command.STATUS_NOT_MODIFIED)
                elif bank_accounts.count() > 1:
                    error = f'Row {row_index+1}: There is more than one bank account with iban "{iban}"'
                    status = self.set_bank_account_status(Command.STATUS_ERROR, error)           
                else:
                    bank_account = BankAccount.objects.create(swift_bic=swift_bic, iban=iban, owner=parent)
                    status = self.set_bank_account_status(Command.STATUS_CREATED)
            else:
                status = self.set_bank_account_status(Command.STATUS_NOT_PROCESSED)
            
            if default_account and family and family.default_bank_account != bank_account:
                self.set_bank_account_status(Command.STATUS_UPDATED_AS_DEFAULT)
                family.default_bank_account = bank_account
                family.save()
                set_as_default = True

        except Exception as e:
            self.logger.error(traceback.format_exc())
            error = f'Row {row_index+1}: Exception processing bank account of parent {parent_number}: {e}'
            status = self.set_bank_account_status(Command.STATUS_ERROR, error)
        finally:
            default_status = 'Set as default' if set_as_default else ''
            message = f'- Parent {parent_number} bank account: {swift_bic}, {iban}, {default_account} -> {status} {default_status} {error}'
            self.print_status(status, message)

        return bank_account
    
    def import_child1(self, sheet, family, row_index):
        child1_name = Command.clean_surname(sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_NAME_INDEX))
        child1_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_YEAR_INDEX)
        child1_level = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_LEVEL_INDEX)

        self.import_child(child1_name, child1_year, child1_level, family, row_index, 1)

    def import_child2(self, sheet, family, row_index):
        child2_name = Command.clean_surname(sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_NAME_INDEX))
        child2_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_YEAR_INDEX)
        child2_level = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_LEVEL_INDEX)

        self.import_child(child2_name, child2_year, child2_level, family, row_index, 2)

    def import_child3(self, sheet, family, row_index):
        child3_name = Command.clean_surname(sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_NAME_INDEX))
        child3_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_YEAR_INDEX)
        child3_level = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_LEVEL_INDEX)

        self.import_child(child3_name, child3_year, child3_level, family, row_index, 3)

    def import_child4(self, sheet, family, row_index):
        child4_name = Command.clean_surname(sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_NAME_INDEX))
        child4_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_YEAR_INDEX)
        child4_level = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_LEVEL_INDEX)

        self.import_child(child4_name, child4_year, child4_level, family, row_index, 4)

    def import_child5(self, sheet, family, row_index):
        child5_name = Command.clean_surname(sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_NAME_INDEX))
        child5_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_YEAR_INDEX)
        child5_level = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_LEVEL_INDEX)

        self.import_child(child5_name, child5_year, child5_level, family, row_index, 5)

    def import_child(self, name, year_of_birth, level, family, row_index, child_number):
        child = None
        status = Command.STATUS_NOT_PROCESSED
        error = ''
        repetition = None

        try:
            if name and family:
                year_of_birth = int(year_of_birth)
                current_level = Level.parse_level(level)
                repetition = Level.calculate_repetition(current_level, year_of_birth)

                children = Child.objects.by_name_and_family(name, family)
                if children.count() == 1:
                    child = children[0]
                    if child.year_of_birth != year_of_birth or child.repetition != repetition:
                        child.year_of_birth = year_of_birth
                        child.repetition = repetition
                        child.save()
                        status = self.set_child_status(Command.STATUS_UPDATED)
                    else:
                        status = self.set_child_status(Command.STATUS_NOT_MODIFIED)
                elif children.count() > 1:
                    error = f'Row {row_index+1}: There is more than one child with name "{name}" in the family "{family}"'
                    status = self.set_child_status(Command.STATUS_ERROR, error)          
                else:
                    child = Child.objects.create(name=name, year_of_birth=year_of_birth, repetition=repetition, family=family)
                    status = self.set_child_status(Command.STATUS_CREATED)
            else:
                status = self.set_child_status(Command.STATUS_NOT_PROCESSED)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            error = f'Row {row_index+1}: Exception processing child {child_number}: {e}'
            status = self.set_child_status(Command.STATUS_ERROR, error)
        finally:
            message = f'- Child {child_number}: {name}, {year_of_birth}, {level} ({repetition}) -> {status} {error}'
            self.print_status(status, message)

        return child

    def set_family_status(self, status, error=None):
        return self.set_status(status, Family.__name__, error)

    def set_parent_status(self, status, error=None):
        return self.set_status(status, Parent.__name__, error)

    def set_child_status(self, status, error=None):
        return self.set_status(status, Child.__name__, error)

    def set_bank_account_status(self, status, error=None):
        return self.set_status(status, BankAccount.__name__, error)

    def set_status(self, status, object_name, error=None):
        if error:
            self.processing_errors.append(error)
        
        if object_name not in self.processed_objects:
            self.processed_objects[object_name] = {}
        
        if status not in self.processed_objects[object_name]:
            self.processed_objects[object_name][status] = 0
        
        self.processed_objects[object_name][status] += 1

        return status

    def get_status_total(self, status, object_name):
        return self.processed_objects.get(object_name, {}).get(status, 0)
    
    def set_totals_before(self):
        if self.TOTAL_BEFORE not in self.totals:
            self.totals[self.TOTAL_BEFORE] = {}

        self.totals[self.TOTAL_BEFORE][Family.__name__] = Family.objects.count()
        self.totals[self.TOTAL_BEFORE][Parent.__name__] = Parent.objects.count()
        self.totals[self.TOTAL_BEFORE][Child.__name__] = Child.objects.count()
        self.totals[self.TOTAL_BEFORE][BankAccount.__name__] = BankAccount.objects.count()
    
    def set_totals_after(self):
        if self.TOTAL_AFTER not in self.totals:
            self.totals[self.TOTAL_AFTER] = {}

        self.totals[self.TOTAL_AFTER][Family.__name__] = Family.objects.count()
        self.totals[self.TOTAL_AFTER][Parent.__name__] = Parent.objects.count()
        self.totals[self.TOTAL_AFTER][Child.__name__] = Child.objects.count()
        self.totals[self.TOTAL_AFTER][BankAccount.__name__] = BankAccount.objects.count()
    
    def get_totals(self, object_name):
        return f'{self.totals[self.TOTAL_BEFORE][object_name]} -> {self.totals[self.TOTAL_AFTER][object_name]}'
