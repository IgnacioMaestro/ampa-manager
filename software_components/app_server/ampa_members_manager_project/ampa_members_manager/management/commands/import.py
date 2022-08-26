import xlrd
import traceback

from django.core.management.base import BaseCommand
from ampa_members_manager.family.models.family import Family


class Command(BaseCommand):
    help = 'Import families, parents, childs and bank accounts from an excel file'

    SHEET_NUMBER = 0
    FIRST_ROW_NUMBER = 2
    FAMILY_SURNAMES_INDEX = 0
    FAMILY_EMAIL1_INDEX = 1
    FAMILY_EMAIL2_INDEX = 2

    PARENT1_FULL_NAME_INDEX = 3
    PARENT1_PHONE1_INDEX = 4
    PARENT1_PHONE2_INDEX = 5
    PARENT1_SWIFT_BIC_INDEX = 6
    PARENT1_IBAN_INDEX = 7
    PARENT1_IS_DEFAULT_INDEX = 8

    PARENT2_FULL_NAME_INDEX = 9
    PARENT2_PHONE1_INDEX = 10
    PARENT2_PHONE2_INDEX = 11
    PARENT2_SWIFT_BIC_INDEX = 12
    PARENT2_IBAN_INDEX = 13
    PARENT2_IS_DEFAULT_INDEX = 14

    CHILD1_NAME_INDEX = 15
    CHILD1_YEAR_INDEX = 16
    CHILD1_REPETITIONS_INDEX = 17

    CHILD2_NAME_INDEX = 18
    CHILD2_YEAR_INDEX = 19
    CHILD2_REPETITIONS_INDEX = 20

    CHILD3_NAME_INDEX = 21
    CHILD3_YEAR_INDEX = 22
    CHILD3_REPETITIONS_INDEX = 23

    CHILD4_NAME_INDEX = 24
    CHILD4_YEAR_INDEX = 25
    CHILD4_REPETITIONS_INDEX = 26

    CHILD5_NAME_INDEX = 27
    CHILD5_YEAR_INDEX = 28
    CHILD5_REPETITIONS_INDEX = 29

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

        sheet = book.sheet_by_index(self.SHEET_NUMBER)
        self.stdout.write(self.style.SUCCESS('Importing rows {}-{} from sheet "{}". Rows: {}. Cols: {}'.format(self.FIRST_ROW_NUMBER, sheet.nrows-1, sheet.name, sheet.nrows, sheet.ncols)))

        for row_index in range(self.FIRST_ROW_NUMBER, sheet.nrows):
            self.stdout.write(self.style.SUCCESS('Row {}'.format(row_index)))

            self.import_family(sheet, row_index)

            self.import_parent1(sheet, row_index)
            self.import_parent1_bank_account(sheet, row_index)

            self.import_parent2(sheet, row_index)
            self.import_parent2_bank_account(sheet, row_index)

            self.import_child1(sheet, row_index)
            self.import_child2(sheet, row_index)
            self.import_child3(sheet, row_index)
            self.import_child4(sheet, row_index)
            self.import_child5(sheet, row_index)

    def import_family(self, sheet, row_index):
        family_surnames = sheet.cell_value(rowx=row_index, colx=self.FAMILY_SURNAMES_INDEX)
        family_email1 = sheet.cell_value(rowx=row_index, colx=self.FAMILY_EMAIL1_INDEX)
        family_email2 = sheet.cell_value(rowx=row_index, colx=self.FAMILY_EMAIL2_INDEX)
        print('- Family: {}, {}, {}'.format(family_surnames, family_email1, family_email2))

        families = Family.objects.filter(surnames=family_surnames)
        if families.count() > 0:
            # TODO: identify family
            # family = families[0]
            # family.surnames = family_surnames
            # family.email = family_email1
            # family.secondary_email = family_email2
            # family.save()
            pass
        else:
            # family = Family.objects.create(surnames=family_surnames, email=family_email1, secondary_email=family_email2)
            pass

    def import_parent1(self, sheet, row_index):
        parent1_full_name = sheet.cell_value(rowx=row_index, colx=self.PARENT1_FULL_NAME_INDEX)
        parent1_phone1 = sheet.cell_value(rowx=row_index, colx=self.PARENT1_PHONE1_INDEX)
        parent1_phone2 = sheet.cell_value(rowx=row_index, colx=self.PARENT1_PHONE2_INDEX)
        print('- Parent 1: {}, {}, {}'.format(parent1_full_name, parent1_phone1, parent1_phone2))

    def import_parent1_bank_account(self, sheet, row_index):
        parent1_swift_bic = sheet.cell_value(rowx=row_index, colx=self.PARENT1_SWIFT_BIC_INDEX)
        parent1_iban = sheet.cell_value(rowx=row_index, colx=self.PARENT1_IBAN_INDEX)
        parent1_is_default_account = sheet.cell_value(rowx=row_index, colx=self.PARENT1_IS_DEFAULT_INDEX)
        print('- Parent 1 bank account: {}, {}, {}'.format(parent1_swift_bic, parent1_iban, parent1_is_default_account))

    def import_parent2(self, sheet, row_index):
        parent2_full_name = sheet.cell_value(rowx=row_index, colx=self.PARENT2_FULL_NAME_INDEX)
        parent2_phone1 = sheet.cell_value(rowx=row_index, colx=self.PARENT2_PHONE1_INDEX)
        parent2_phone2 = sheet.cell_value(rowx=row_index, colx=self.PARENT2_PHONE2_INDEX)
        print('- Parent 2: {}, {}, {}'.format(parent2_full_name, parent2_phone1, parent2_phone2))

    def import_parent2_bank_account(self, sheet, row_index):
        parent2_swift_bic = sheet.cell_value(rowx=row_index, colx=self.PARENT2_SWIFT_BIC_INDEX)
        parent2_iban = sheet.cell_value(rowx=row_index, colx=self.PARENT2_IBAN_INDEX)
        parent2_is_default_account = sheet.cell_value(rowx=row_index, colx=self.PARENT2_IS_DEFAULT_INDEX)
        print('- Parent 2 bank account: {}, {}, {}'.format(parent2_swift_bic, parent2_iban, parent2_is_default_account))
    
    def import_child1(self, sheet, row_index):
        child1_name = sheet.cell_value(rowx=row_index, colx=self.CHILD1_NAME_INDEX)
        child1_year = sheet.cell_value(rowx=row_index, colx=self.CHILD1_YEAR_INDEX)
        child1_repetitions = sheet.cell_value(rowx=row_index, colx=self.CHILD1_REPETITIONS_INDEX)
        print('- Child 1: {}, {}, {}'.format(child1_name, child1_year, child1_repetitions))

        self.import_child(child1_name, child1_year, child1_repetitions)

    def import_child2(self, sheet, row_index):
        child2_name = sheet.cell_value(rowx=row_index, colx=self.CHILD2_NAME_INDEX)
        child2_year = sheet.cell_value(rowx=row_index, colx=self.CHILD2_YEAR_INDEX)
        child2_repetitions = sheet.cell_value(rowx=row_index, colx=self.CHILD2_REPETITIONS_INDEX)
        print('- Child 2: {}, {}, {}'.format(child2_name, child2_year, child2_repetitions))

        self.import_child(child2_name, child2_year, child2_repetitions)

    def import_child3(self, sheet, row_index):
        child3_name = sheet.cell_value(rowx=row_index, colx=self.CHILD3_NAME_INDEX)
        child3_year = sheet.cell_value(rowx=row_index, colx=self.CHILD3_YEAR_INDEX)
        child3_repetitions = sheet.cell_value(rowx=row_index, colx=self.CHILD3_REPETITIONS_INDEX)
        print('- Child 3: {}, {}, {}'.format(child3_name, child3_year, child3_repetitions))

        self.import_child(child3_name, child3_year, child3_repetitions)

    def import_child4(self, sheet, row_index):
        child4_name = sheet.cell_value(rowx=row_index, colx=self.CHILD4_NAME_INDEX)
        child4_year = sheet.cell_value(rowx=row_index, colx=self.CHILD4_YEAR_INDEX)
        child4_repetitions = sheet.cell_value(rowx=row_index, colx=self.CHILD4_REPETITIONS_INDEX)
        print('- Child 4: {}, {}, {}'.format(child4_name, child4_year, child4_repetitions))

        self.import_child(child4_name, child4_year, child4_repetitions)

    def import_child5(self, sheet, row_index):
        child5_name = sheet.cell_value(rowx=row_index, colx=self.CHILD5_NAME_INDEX)
        child5_year = sheet.cell_value(rowx=row_index, colx=self.CHILD5_YEAR_INDEX)
        child5_repetitions = sheet.cell_value(rowx=row_index, colx=self.CHILD5_REPETITIONS_INDEX)
        print('- Child 5: {}, {}, {}'.format(child5_name, child5_year, child5_repetitions))
        
        self.import_child(child5_name, child5_year, child5_repetitions)

    def import_child(self, name, year, repetitions):
        pass
