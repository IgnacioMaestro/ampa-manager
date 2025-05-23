import traceback
from datetime import datetime

import xlrd
from django.core.management.base import BaseCommand

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.utils.fields_formatters import FieldsFormatters


class Command(BaseCommand):
    help = 'Import bank account authorizations'

    SHEET_NUMBER = 0
    FIRST_ROW_NUMBER = 0
    PARENT_FULL_NAME_INDEX = 0
    IBAN_INDEX = 1
    NUMBER_INDEX = 2
    DATE_INDEX = 3

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            self.load_excel(options['file'])

            self.importer = AuthorizationImporter(self.sheet, self.book)

            errors_count = 0
            success_count = 0
            for row_index in range(Command.FIRST_ROW_NUMBER, self.sheet.nrows):
                success, _ = self.importer.import_authorization(row_index)

                if success:
                    success_count += 1
                else:
                    errors_count += 1

            print(f'\nERRORS: {errors_count}')
            print(f'IMPORTED OK: {success_count}\n')

        except:
            print(traceback.format_exc())

    def load_excel(self, file_path):
        print(f'\nImporting file {file_path}')
        self.book = xlrd.open_workbook(file_path)
        self.sheet = self.book.sheet_by_index(Command.SHEET_NUMBER)


class AuthorizationImporter:

    def __init__(self, sheet, book):
        self.book = book
        self.sheet = sheet

    def import_authorization(self, row_index):
        authorization = None
        success = False
        message = ''

        parent_full_name = None
        iban = None
        number = None
        date_value = None

        try:
            parent_full_name = FieldsFormatters.format_name(
                self.sheet.cell_value(rowx=row_index, colx=Command.PARENT_FULL_NAME_INDEX))
            iban = FieldsFormatters.format_iban(self.sheet.cell_value(rowx=row_index, colx=Command.IBAN_INDEX))
            number = FieldsFormatters.format_string(self.sheet.cell_value(rowx=row_index, colx=Command.NUMBER_INDEX))

            date_value = self.sheet.cell_value(rowx=row_index, colx=Command.DATE_INDEX)
            if date_value not in [None, '']:
                date_value = datetime(*xlrd.xldate_as_tuple(date_value, self.book.datemode))

            if iban and parent_full_name:

                bank_account = AuthorizationImporter.get_bank_account(iban)
                if bank_account:
                    if parent_full_name:
                        parent = AuthorizationImporter.get_parent(parent_full_name)
                        if parent:
                            if number not in [None, '']:
                                if date_value not in [None, '']:
                                    try:
                                        holder: Holder = Holder.objects.get(parent=parent, bank_account=bank_account)
                                        if holder:
                                            holder.authorization_sign_date = date_value
                                            holder.authorization_year = date_value.year
                                            holder.save()

                                            success = True
                                            message = f'Updated'
                                        else:
                                            Holder.objects.create(
                                                parent=parent, bank_account=bank_account, authorization_order=number,
                                                authorization_sign_date=date_value, authorization_year=date_value.year)
                                            success = True
                                            message = f'Created'
                                    except Holder.DoesNotExist:
                                        message = f'Account owner does not match'
                                else:
                                    message = f'Missing date'
                            else:
                                message = f'Missing number'
                        else:
                            message = f'Account owner not found'
                    else:
                        message = f'Parent not found'
                else:
                    message = f'IBAN not found'

        except Exception as e:
            print(traceback.format_exc())
            message = f'Exception: {e}'
        finally:
            status = 'OK' if success else 'ERROR'
            print(f'- Row {row_index + 1}: {parent_full_name}, {iban}, {number}, {date_value} -> {status}: {message}')

        return success, authorization

    @staticmethod
    def get_parent(full_name):
        try:
            return Parent.objects.get(name_and_surnames=full_name)
        except Parent.DoesNotExist:
            return None

    @staticmethod
    def get_bank_account(iban):
        try:
            return BankAccount.objects.get(iban=iban)
        except BankAccount.DoesNotExist:
            return None
