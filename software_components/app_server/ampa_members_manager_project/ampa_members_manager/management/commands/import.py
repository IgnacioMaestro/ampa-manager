import xlrd
import traceback

from django.core.management.base import BaseCommand
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
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

    OBJECT_FAMILY = 'families'
    OBJECT_PARENT = 'parents'
    OBJECT_CHILD = 'children'
    OBJECT_BANK_ACCOUNT = 'bank_accounts'

    processed_objects = {}
    processing_errors = []

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Importing file "{0}"'.format(options['file'])))
            self.import_file(options['file'])
            self.print_stats()
        except:
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def import_file(self, file_path):
        book = xlrd.open_workbook(file_path)

        sheet = book.sheet_by_index(xls_settings.SHEET_NUMBER)
        self.stdout.write(self.style.SUCCESS('Importing rows {}-{} from sheet "{}". Rows: {}. Cols: {}'.format(xls_settings.FIRST_ROW_NUMBER, sheet.nrows-1, sheet.name, sheet.nrows, sheet.ncols)))

        for row_index in range(xls_settings.FIRST_ROW_NUMBER, sheet.nrows):
            self.stdout.write(self.style.SUCCESS('Row {}'.format(row_index)))

            family = self.import_family(sheet, row_index)

            parent1 = self.import_parent1(sheet, family, row_index)
            parent2 = self.import_parent2(sheet, family, row_index)

            self.import_parent1_bank_account(sheet, parent1, family, row_index)
            self.import_parent2_bank_account(sheet, parent2, family, row_index)

            self.import_child1(sheet, family, row_index)
            self.import_child2(sheet, family, row_index)
            self.import_child3(sheet, family, row_index)
            self.import_child4(sheet, family, row_index)
            self.import_child5(sheet, family, row_index)
    
    def print_stats(self):
        self.stdout.write(self.style.SUCCESS(f'Families:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_CREATED, Command.OBJECT_FAMILY)} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_UPDATED, Command.OBJECT_FAMILY)} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_NOT_MODIFIED, Command.OBJECT_FAMILY)} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_ERROR, Command.OBJECT_FAMILY)} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Parents:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_CREATED, Command.OBJECT_PARENT)} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_UPDATED, Command.OBJECT_PARENT)} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_NOT_MODIFIED, Command.OBJECT_PARENT)} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_UPDATED_ADDED_TO_FAMILY, Command.OBJECT_PARENT)} assigned to a family. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_ERROR, Command.OBJECT_PARENT)} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Children:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_CREATED, Command.OBJECT_CHILD)} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_UPDATED, Command.OBJECT_CHILD)} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_NOT_MODIFIED, Command.OBJECT_CHILD)} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_ERROR, Command.OBJECT_CHILD)} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Bank accounts:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_CREATED, Command.OBJECT_BANK_ACCOUNT)} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_UPDATED, Command.OBJECT_BANK_ACCOUNT)} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_NOT_MODIFIED, Command.OBJECT_BANK_ACCOUNT)} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_UPDATED_AS_DEFAULT, Command.OBJECT_BANK_ACCOUNT)} family default bank accounts changed. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.get_status(Command.STATUS_ERROR, Command.OBJECT_BANK_ACCOUNT)} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Errors:'))
        if len(self.processing_errors) > 0:
            for error in self.processing_errors:
                self.stdout.write(self.style.ERROR(f'- {error} '))
        else:
            self.stdout.write(self.style.SUCCESS(f'- No errors'))

    def print_status(self, status, message):
        if status == Command.STATUS_ERROR:
            self.stdout.write(self.style.ERROR(message))
        elif status == Command.STATUS_NOT_PROCESSED:
            self.stdout.write(self.style.WARNING(message))
        else:
            self.stdout.write(self.style.SUCCESS(message))

    def import_family(self, sheet, row_index):
        family = None
        status = Command.STATUS_NOT_PROCESSED
        error = ''

        try:
            family_surnames = sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_SURNAMES_INDEX).strip()
            family_email1 = sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_EMAIL1_INDEX).strip()
            family_email2 = sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_EMAIL2_INDEX).strip()

            if family_surnames:
                families = Family.objects.filter(surnames__iexact=family_surnames)
                if families.count() == 1:
                    family = families[0]
                    if family.email != family_email1 or family.secondary_email != family_email2:
                        family.email = family_email1
                        family.secondary_email = family_email2
                        family.save()
                        status = self.set_family_status(Command.STATUS_UPDATED)
                    else:
                        status = self.set_family_status(Command.STATUS_NOT_MODIFIED)
                elif families.count() > 1:
                    error = f'Row {row_index}: There is more than one family with surnames "{family_surnames}"'
                    status = self.set_family_status(Command.STATUS_ERROR, error)
                else:
                    family = Family.objects.create(surnames=family_surnames, email=family_email1, secondary_email=family_email2)
                    status = self.set_family_status(Command.STATUS_CREATED)
            else:
                error = f'Row {row_index}: Family without surnames'
                status = self.set_family_status(Command.STATUS_ERROR, error)
        except Exception as e:
            error = f'Row {row_index}: Exception processing family: {e}'
            status = self.set_family_status(Command.STATUS_ERROR, error)
        finally:
            message = f'- Family: {family_surnames}, {family_email1}, {family_email2} -> {status} {error}'
            self.print_status(status, message)

        return family

    def import_parent1(self, sheet, family, row_index):
        parent1_full_name = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_FULL_NAME_INDEX).strip()
        parent1_phone1 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_PHONE1_INDEX).strip()
        parent1_phone2 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_PHONE2_INDEX).strip()

        return self.import_parent(parent1_full_name, parent1_phone1, parent1_phone2, family, row_index, 1)

    def import_parent2(self, sheet, family, row_index):
        parent2_full_name = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_FULL_NAME_INDEX).strip()
        parent2_phone1 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_PHONE1_INDEX).strip()
        parent2_phone2 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_PHONE2_INDEX).strip()

        return self.import_parent(parent2_full_name, parent2_phone1, parent2_phone2, family, row_index, 2)

    def import_parent(self, full_name, phone1, phone2, family, row_index, parent_number):
        parent = None
        status = Command.STATUS_NOT_PROCESSED
        error = ''

        try:
            if full_name:
                parents = Parent.objects.filter(name_and_surnames__iexact=full_name)
                if parents.count() == 1:
                    parent = parents[0]
                    if parent.phone_number != phone1 or parent.additional_phone_number != phone2:
                        parent.phone_number = phone1
                        parent.additional_phone_number = phone2
                        parent.save()
                        status = self.set_parent_status(Command.STATUS_UPDATED)
                    else:
                        status = self.set_parent_status(Command.STATUS_NOT_MODIFIED)
                elif parents.count() > 1:
                    error = f'Row {row_index}: There is more than one parent with name "{full_name}"'
                    status = self.set_parent_status(Command.STATUS_ERROR)
                else:
                    parent = Parent.objects.create(name_and_surnames=full_name, phone_number=phone1, additional_phone_number=phone2)
                    status = self.set_parent_status(Command.STATUS_CREATED)
                
                if not parent.family_set.filter(surnames=family.surnames).exists():
                    status = self.set_parent_status(Command.STATUS_UPDATED_ADDED_TO_FAMILY)
                    family.parents.add(parent)
            else:
                error = f'Row {row_index}: Parent without name'
                status = self.set_parent_status(Command.STATUS_ERROR)
        except Exception as e:
            error = f'Row {row_index}: Exception processing parent {parent_number}: {e}'
            status = self.set_parent_status(Command.STATUS_ERROR)
        finally:
            message = f'- Parent {parent_number}: {full_name}, {phone1}, {phone2} -> {status} {error}'
            self.print_status(status, message)

        return parent

    def import_parent1_bank_account(self, sheet, parent, family, row_index):
        parent1_swift_bic = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_SWIFT_BIC_INDEX)
        parent1_iban = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_IBAN_INDEX)
        parent1_is_default_account = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_IS_DEFAULT_INDEX)

        self.import_bank_account(parent1_swift_bic, parent1_iban, parent1_is_default_account, parent, family, row_index, 1)

    def import_parent2_bank_account(self, sheet, parent, family, row_index):
        parent2_swift_bic = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_SWIFT_BIC_INDEX)
        parent2_iban = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_IBAN_INDEX)
        parent2_is_default_account = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_IS_DEFAULT_INDEX)

        self.import_bank_account(parent2_swift_bic, parent2_iban, parent2_is_default_account, parent, family, row_index, 2)
    
    def str_to_bool(self, str_bool):
        if str_bool:
            return str_bool.strip().lower() in ["si", "sí", "yes", "1", "true"]
        else:
            return False
    
    def import_bank_account(self, swift_bic, iban, default_account, parent, family, row_index, parent_number):
        bank_account = None
        status = Command.STATUS_NOT_PROCESSED
        error = ''

        try:
            swift_bic = swift_bic.strip()
            iban = iban.strip()
            default_account = self.str_to_bool(default_account)

            if swift_bic and iban:
                bank_accounts = BankAccount.objects.filter(iban=iban)
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
                    error = f'Row {row_index}: There is more than one bank account with iban "{iban}"'
                    status = self.set_bank_account_status(Command.STATUS_ERROR, error)           
                else:
                    bank_account = BankAccount.objects.create(swift_bic=swift_bic, iban=iban, owner=parent)
                    status = self.set_bank_account_status(Command.STATUS_CREATED)
            else:
                error = f'Row {row_index}: Account without iban or swift code'
                status = self.set_bank_account_status(Command.STATUS_ERROR, error)
            
            if default_account and family.default_bank_account != bank_account:
                status = self.set_bank_account_status(Command.STATUS_UPDATED_AS_DEFAULT)
                family.default_bank_account = bank_account
                family.save()

        except Exception as e:
            error = f'Row {row_index}: Exception processing bank account of parent {parent_number}: {e}'
            status = self.set_bank_account_status(Command.STATUS_ERROR, error)
        finally:
            message = f'- Parent {parent_number} bank account: {swift_bic}, {iban}, {default_account} -> {status} {error}'
            self.print_status(status, message)

        return bank_account
    
    def import_child1(self, sheet, family, row_index):
        child1_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_NAME_INDEX)
        child1_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_YEAR_INDEX)
        child1_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_REPETITIONS_INDEX)

        self.import_child(child1_name, child1_year, child1_repetitions, family, row_index, 1)

    def import_child2(self, sheet, family, row_index):
        child2_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_NAME_INDEX)
        child2_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_YEAR_INDEX)
        child2_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_REPETITIONS_INDEX)

        self.import_child(child2_name, child2_year, child2_repetitions, family, row_index, 2)

    def import_child3(self, sheet, family, row_index):
        child3_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_NAME_INDEX)
        child3_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_YEAR_INDEX)
        child3_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_REPETITIONS_INDEX)

        self.import_child(child3_name, child3_year, child3_repetitions, family, row_index, 3)

    def import_child4(self, sheet, family, row_index):
        child4_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_NAME_INDEX)
        child4_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_YEAR_INDEX)
        child4_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_REPETITIONS_INDEX)

        self.import_child(child4_name, child4_year, child4_repetitions, family, row_index, 4)

    def import_child5(self, sheet, family, row_index):
        child5_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_NAME_INDEX)
        child5_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_YEAR_INDEX)
        child5_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_REPETITIONS_INDEX)

        self.import_child(child5_name, child5_year, child5_repetitions, family, row_index, 5)

    def import_child(self, name, year, repetition, family, row_index, child_number):
        child = None
        status = Command.STATUS_NOT_PROCESSED
        error = ''

        try:
            if name and family:
                year = int(year)
                repetition = int(repetition)

                children = Child.objects.filter(name__iexact=name, family=family)
                if children.count() == 1:
                    child = children[0]
                    if child.year_of_birth != year or child.repetition != repetition:
                        child.year_of_birth = year
                        child.repetition = repetition
                        child.save()
                        status = self.set_child_status(Command.STATUS_UPDATED)
                    else:
                        status = self.set_child_status(Command.STATUS_NOT_MODIFIED)
                elif children.count() > 1:
                    error = f'Row {row_index}: There is more than one child with name "{name}" in the family "{family}"'
                    status = self.set_child_status(Command.STATUS_ERROR, error)          
                else:
                    child = Child.objects.create(name=name, year_of_birth=year, repetition=repetition, family=family)
                    status = self.set_child_status(Command.STATUS_CREATED)
            else:
                status = self.set_child_status(Command.STATUS_NOT_PROCESSED)
        except Exception as e:
            error = f'Row {row_index}: Exception processing child {child_number}: {e}'
            status = self.set_child_status(Command.STATUS_ERROR, error)
        finally:
            message = f'- Child {child_number}: {name}, {year}, {repetition} -> {status} {error}'
            self.print_status(status, message)

        return child

    def set_family_status(self, status, error=None):
        return self.set_status(status, Command.OBJECT_FAMILY, error)

    def set_parent_status(self, status, error=None):
        return self.set_status(status, Command.OBJECT_PARENT, error)

    def set_child_status(self, status, error=None):
        return self.set_status(status, Command.OBJECT_CHILD, error)

    def set_bank_account_status(self, status, error=None):
        return self.set_status(status, Command.OBJECT_BANK_ACCOUNT, error)

    def set_status(self, status, object_name, error=None):
        if error:
            self.processing_errors.append(error)
        
        if object_name not in self.processed_objects:
            self.processed_objects[object_name] = {}
        
        if status not in self.processed_objects[object_name]:
            self.processed_objects[object_name][status] = 0
        
        self.processed_objects[object_name][status] += 1

        return status

    def get_status(self, status, object_name):
        return self.processed_objects.get(object_name, {}).get(status, 0)