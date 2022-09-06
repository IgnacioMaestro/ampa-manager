import xlrd
import traceback

from django.core.management.base import BaseCommand
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
import members_excel_settings as xls_settings


class Command(BaseCommand):
    help = 'Import families, parents, childs and bank accounts from an excel file'

    processed_objects = {
        'families': {
            'created': 0,
            'updated': 0,
            'not_modified': 0,
            'error': 0
        },
        'parents': {
            'created': 0,
            'updated': 0,
            'not_modified': 0,
            'added_to_family': 0,
            'error': 0
        },
        'children': {
            'created': 0,
            'updated': 0,
            'not_modified': 0,
            'error': 0
        },
        'bank_accounts': {
            'created': 0,
            'updated': 0,
            'not_modified': 0,
            'set_as_default': 0,
            'error': 0
        }
    }

    processing_errors = []

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Importing file "{0}"'.format(options['file'])))
            self.import_file(options['file'])
            self.stdout.write(self.style.SUCCESS('Successfully imported'))
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
        
        self.print_stats()
    
    def print_stats(self):
        self.stdout.write(self.style.SUCCESS(f'Families:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["families"]["created"]} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["families"]["updated"]} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["families"]["not_modified"]} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["families"]["error"]} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Parents:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["parents"]["created"]} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["parents"]["updated"]} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["parents"]["not_modified"]} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["parents"]["added_to_family"]} assigned to a family. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["parents"]["error"]} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Children:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["children"]["created"]} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["children"]["updated"]} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["children"]["not_modified"]} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["children"]["error"]} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Bank accounts:'))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["bank_accounts"]["created"]} created. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["bank_accounts"]["updated"]} updated. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["bank_accounts"]["not_modified"]} not modified. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["bank_accounts"]["set_as_default"]} set as family default account. '))
        self.stdout.write(self.style.SUCCESS(f'- {self.processed_objects["bank_accounts"]["error"]} errors. '))

        self.stdout.write(self.style.SUCCESS(f'Errors:'))
        for error in self.processing_errors:
            self.stdout.write(self.style.ERROR(f'- {error} '))

    def import_family(self, sheet, row_index):
        family = None

        try:
            family_surnames = sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_SURNAMES_INDEX).strip()
            family_email1 = sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_EMAIL1_INDEX).strip()
            family_email2 = sheet.cell_value(rowx=row_index, colx=xls_settings.FAMILY_EMAIL2_INDEX).strip()
            print('- Family: {}, {}, {}'.format(family_surnames, family_email1, family_email2))

            if family_surnames:
                families = Family.objects.filter(surnames__iexact=family_surnames)
                if families.count() == 1:
                    family = families[0]
                    if family.email != family_email1 or family.secondary_email != family_email2:
                        family.email = family_email1
                        family.secondary_email = family_email2
                        family.save()
                        self.processed_objects['families']['updated'] += 1
                    else:
                        self.processed_objects['families']['not_modified'] += 1
                elif families.count() > 1:
                    error = f'Row {row_index}: There is more than one family with surnames "{family_surnames}"'
                    self.processing_errors.append(error)
                    self.processed_objects['families']['error'] += 1                
                else:
                    family = Family.objects.create(surnames=family_surnames, email=family_email1, secondary_email=family_email2)
                    self.processed_objects['families']['created'] += 1
            else:
                error = f'Row {row_index}: Family without surnames'
                self.processing_errors.append(error)
                self.processed_objects['families']['error'] += 1
        except Exception as e:
            error = f'Row {row_index}: Exception processing family: {e}'
            self.processing_errors.append(error)
            self.processed_objects['families']['error'] += 1

        return family

    def import_parent1(self, sheet, family, row_index):
        parent1_full_name = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_FULL_NAME_INDEX).strip()
        parent1_phone1 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_PHONE1_INDEX).strip()
        parent1_phone2 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_PHONE2_INDEX).strip()
        print('- Parent 1: {}, {}, {}'.format(parent1_full_name, parent1_phone1, parent1_phone2))

        return self.import_parent(parent1_full_name, parent1_phone1, parent1_phone2, family, row_index)

    def import_parent2(self, sheet, family, row_index):
        parent2_full_name = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_FULL_NAME_INDEX).strip()
        parent2_phone1 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_PHONE1_INDEX).strip()
        parent2_phone2 = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_PHONE2_INDEX).strip()
        print('- Parent 2: {}, {}, {}'.format(parent2_full_name, parent2_phone1, parent2_phone2))

        return self.import_parent(parent2_full_name, parent2_phone1, parent2_phone2, family, row_index)

    def import_parent(self, full_name, phone1, phone2, family, row_index):
        parent = None

        try:
            if full_name:
                parents = Parent.objects.filter(name_and_surnames__iexact=full_name)
                if parents.count() == 1:
                    parent = parents[0]
                    if parent.phone_number != phone1 or parent.additional_phone_number != phone2:
                        parent.phone_number = phone1
                        parent.additional_phone_number = phone2
                        parent.save()
                        self.processed_objects['parents']['updated'] += 1
                    else:
                        self.processed_objects['parents']['not_modified'] += 1
                elif parents.count() > 1:
                    error = f'Row {row_index}: There is more than one parent with name "{full_name}"'
                    self.processing_errors.append(error)
                    self.processed_objects['parents']['error'] += 1                
                else:
                    parent = Parent.objects.create(name_and_surnames=full_name, phone_number=phone1, additional_phone_number=phone2)
                    self.processed_objects['parents']['created'] += 1
                
                if not parent.family_set.filter(surnames=family.surnames).exists():
                    self.processed_objects['parents']['added_to_family'] += 1
                    family.parents.add(parent)
            else:
                error = f'Row {row_index}: Parent without name'
                self.processing_errors.append(error)
                self.processed_objects['parents']['error'] += 1
        except Exception as e:
            error = f'Row {row_index}: Exception processing parent with name "{full_name}": {e}'
            self.processing_errors.append(error)
            self.processed_objects['parents']['error'] += 1

        return parent

    def import_parent1_bank_account(self, sheet, parent, family, row_index):
        parent1_swift_bic = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_SWIFT_BIC_INDEX).strip()
        parent1_iban = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_IBAN_INDEX).strip()
        parent1_is_default_account = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT1_IS_DEFAULT_INDEX).strip()
        print('- Parent 1 bank account: {}, {}, {}'.format(parent1_swift_bic, parent1_iban, parent1_is_default_account))

        self.import_bank_account(parent1_swift_bic, parent1_iban, parent1_is_default_account, parent, family, row_index)

    def import_parent2_bank_account(self, sheet, parent, family, row_index):
        parent2_swift_bic = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_SWIFT_BIC_INDEX).strip()
        parent2_iban = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_IBAN_INDEX).strip()
        parent2_is_default_account = sheet.cell_value(rowx=row_index, colx=xls_settings.PARENT2_IS_DEFAULT_INDEX).strip()
        print('- Parent 2 bank account: {}, {}, {}'.format(parent2_swift_bic, parent2_iban, parent2_is_default_account))

        self.import_bank_account(parent2_swift_bic, parent2_iban, parent2_is_default_account, parent, family, row_index)
    
    def import_bank_account(self, swift_bic, iban, default_account, parent, family, row_index):
        bank_account = None
        try:
            if swift_bic and iban:
                bank_accounts = BankAccount.objects.filter(iban=iban)
                if bank_accounts.count() == 1:
                    bank_account = bank_accounts[0]
                    if bank_account.swift_bic != swift_bic or bank_account.owner != parent:
                        bank_account.swift_bic = swift_bic
                        bank_account.owner = parent
                        bank_account.save()
                        self.processed_objects['bank_accounts']['updated'] += 1
                    else:
                        self.processed_objects['bank_accounts']['not_modified'] += 1
                elif bank_accounts.count() > 1:
                    error = f'Row {row_index}: There is more than one bank account with iban "{iban}"'
                    self.processing_errors.append(error)
                    self.processed_objects['bank_accounts']['error'] += 1                
                else:
                    bank_account = BankAccount.objects.create(swift_bic=swift_bic, iban=iban, owner=parent)
                    self.processed_objects['bank_accounts']['created'] += 1
            else:
                error = f'Row {row_index}: Account without iban or swift code'
                self.processing_errors.append(error)
                self.processed_objects['bank_accounts']['error'] += 1
            
            if default_account and family.default_bank_account != bank_account:
                self.processed_objects['bank_accounts']['set_as_default'] += 1
                family.default_bank_account = bank_account
                family.save()

        except Exception as e:
            error = f'Row {row_index}: Exception processing bank account with iban "{iban}": {e}'
            self.processing_errors.append(error)
            self.processed_objects['bank_accounts']['error'] += 1

        return bank_account
    
    def import_child1(self, sheet, family, row_index):
        child1_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_NAME_INDEX)
        child1_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_YEAR_INDEX)
        child1_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD1_REPETITIONS_INDEX)
        print('- Child 1: {}, {}, {}'.format(child1_name, child1_year, child1_repetitions))

        self.import_child(child1_name, child1_year, child1_repetitions, family, row_index)

    def import_child2(self, sheet, family, row_index):
        child2_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_NAME_INDEX)
        child2_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_YEAR_INDEX)
        child2_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD2_REPETITIONS_INDEX)
        print('- Child 2: {}, {}, {}'.format(child2_name, child2_year, child2_repetitions))

        self.import_child(child2_name, child2_year, child2_repetitions, family, row_index)

    def import_child3(self, sheet, family, row_index):
        child3_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_NAME_INDEX)
        child3_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_YEAR_INDEX)
        child3_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD3_REPETITIONS_INDEX)
        print('- Child 3: {}, {}, {}'.format(child3_name, child3_year, child3_repetitions))

        self.import_child(child3_name, child3_year, child3_repetitions, family, row_index)

    def import_child4(self, sheet, family, row_index):
        child4_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_NAME_INDEX)
        child4_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_YEAR_INDEX)
        child4_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD4_REPETITIONS_INDEX)
        print('- Child 4: {}, {}, {}'.format(child4_name, child4_year, child4_repetitions))

        self.import_child(child4_name, child4_year, child4_repetitions, family, row_index)

    def import_child5(self, sheet, family, row_index):
        child5_name = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_NAME_INDEX)
        child5_year = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_YEAR_INDEX)
        child5_repetitions = sheet.cell_value(rowx=row_index, colx=xls_settings.CHILD5_REPETITIONS_INDEX)
        print('- Child 5: {}, {}, {}'.format(child5_name, child5_year, child5_repetitions))
        
        self.import_child(child5_name, child5_year, child5_repetitions, family, row_index)

    def import_child(self, name, year, repetition, family, row_index):
        child = None

        try:
            if name and family:
                children = Child.objects.filter(name__iexact=name, family=family)
                if children.count() == 1:
                    child = children[0]
                    if child.year_of_birth != year or child.repetition != repetition:
                        child.year_of_birth = year
                        child.repetition = repetition
                        child.save()
                        self.processed_objects['children']['updated'] += 1
                    else:
                        self.processed_objects['children']['not_modified'] += 1
                elif children.count() > 1:
                    error = f'Row {row_index}: There is more than one child with name "{name}" in the family "{family}"'
                    self.processing_errors.append(error)
                    self.processed_objects['children']['error'] += 1                
                else:
                    child = Child.objects.create(name=name, year_of_birth=year, repetition=repetition, family=family)
                    self.processed_objects['children']['created'] += 1
            else:
                error = f'Row {row_index}: Child without name or family'
                self.processing_errors.append(error)
                self.processed_objects['children']['error'] += 1
        except Exception as e:
            error = f'Row {row_index}: Exception processing child with name "{name}": {e}'
            self.processing_errors.append(error)
            self.processed_objects['children']['error'] += 1

        return child
