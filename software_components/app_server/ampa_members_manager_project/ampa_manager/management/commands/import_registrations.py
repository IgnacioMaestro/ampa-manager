import traceback

from django.core.management.base import BaseCommand

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.use_cases.import_after_school.after_school_importer import AfterSchoolImporter
from ampa_manager.activity.use_cases.import_edition.after_school_edition_importer import AfterSchoolEditionImporter
from ampa_manager.activity.use_cases.import_registration.after_school_registration_importer import \
    AfterSchoolRegistrationImporter
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.import_bank_account.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.import_child.child_importer import ChildImporter
from ampa_manager.family.use_cases.import_family.family_importer import FamilyImporter
from ampa_manager.family.use_cases.import_parent.parent_importer import ParentImporter
from ampa_manager.management.commands.importers.registration_excel_importer import RegistrationExcelImporter, \
    RegistrationImportResult, RegistrationExcelRow
from ampa_manager.management.commands.utils.logger import Logger


class Command(BaseCommand):
    help = 'Import after-schools registrations'

    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2
    CREATE_EDITION_IF_NOT_EXISTS = True

    def __init__(self):
        super().__init__()
        self.logger = Logger('import_registrations')

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            excel_file_name = options['file']
            excel_importer: RegistrationExcelImporter = RegistrationExcelImporter(excel_file_name, Command.SHEET_NUMBER, Command.FIRST_ROW_INDEX)

            results = []
            counters_before = Command.count_objects()
            registration_row: RegistrationExcelRow
            for registration_row in excel_importer.import_rows():
                result: RegistrationImportResult = self.import_registration(registration_row)
                result.print(self.logger)
                results.append(result)

            counters_after = Command.count_objects()

            RegistrationImportResult.print_stats(self.logger, results, counters_before, counters_after)

        except:
            self.logger.error(traceback.format_exc())
        finally:
            if self.logger:
                self.logger.close_log_file()

    @staticmethod
    def count_objects():
        return {
            'families': Family.objects.count(),
            'parents': Parent.objects.count(),
            'children': Child.objects.count(),
            'bank_accounts': BankAccount.objects.count(),
            'after_schools': AfterSchool.objects.count(),
            'editions': AfterSchoolEdition.objects.count(),
            'registrations': AfterSchoolRegistration.objects.count()
        }

    def import_registration(self, fields: RegistrationExcelRow) -> RegistrationImportResult:
        result = RegistrationImportResult(fields.row_index)

        try:
            family_result = FamilyImporter.import_family(fields.family_surnames, fields.parent_name_and_surnames)
            result.add_partial_result(family_result)
            if not family_result.success:
                return result

            family = family_result.imported_object
            child_result = ChildImporter.import_child(family, fields.child_name, fields.child_level, fields.child_year_of_birth)
            result.add_partial_result(child_result)
            if not child_result.success:
                return result

            child = child_result.imported_object
            parent_result = ParentImporter.import_parent(family, fields.parent_name_and_surnames,
                                                          fields.parent_phone_number, fields.parent_additional_phone_number,
                                                          fields.parent_email)
            result.add_partial_result(parent_result)
            if not parent_result.success:
                return result

            parent = parent_result.imported_object
            bank_account_result = BankAccountImporter.import_bank_account(parent, fields.bank_account_iban)
            result.add_partial_result(bank_account_result)
            if not bank_account_result.success:
                return result

            bank_account = bank_account_result.imported_object
            after_school_result = AfterSchoolImporter.import_after_school(fields.after_school_name)
            result.add_partial_result(after_school_result)
            if not after_school_result.success:
                return result

            after_school = after_school_result.imported_object
            edition_result = AfterSchoolEditionImporter.import_edition(
                after_school, fields.edition_period, fields.edition_timetable, fields.edition_levels,
                fields.edition_price_for_members, fields.edition_price_for_no_members,
                Command.CREATE_EDITION_IF_NOT_EXISTS)
            result.add_partial_result(edition_result)
            if not edition_result.success:
                return result

            after_school_edition = edition_result.imported_object
            registration_result = AfterSchoolRegistrationImporter.import_registration(after_school_edition, bank_account, child)
            result.add_partial_result(registration_result)

        except Exception as e:
            self.logger.error(f'Row {fields.row_index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result
