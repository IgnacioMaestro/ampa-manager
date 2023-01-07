import traceback

from django.core.management.base import BaseCommand

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.importers.registration_excel_importer import RegistrationExcelImporter, \
    RegistrationImportResult, RegistrationExcelRowFields
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
            excel_importer = RegistrationExcelImporter(excel_file_name, Command.SHEET_NUMBER, Command.FIRST_ROW_INDEX)

            results = []
            counts_before = Command.count_objects()
            for registration_fields in excel_importer.get_data():
                result = self.import_registration(registration_fields)
                result.print(self.logger)
                results.append(result)

            counts_after = Command.count_objects()

            RegistrationImportResult.print_stats(self.logger, results, counts_before, counts_after)

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

    def import_registration(self, fields: RegistrationExcelRowFields):
        result = RegistrationImportResult(fields.row_index)

        try:
            partial_result = Family.import_family(fields.family_surnames, fields.parent_name_and_surnames)
            if partial_result.success:
                family = partial_result.imported_object
            else:
                return result

            child, result.child_state, result.error = Child.import_child(family, fields.child_name, fields.child_level,
                                                                         fields.child_year_of_birth)
            if not child:
                return result

            parent, result.parent_state, result.error = Parent.import_parent(family,
                                                                             fields.parent_name_and_surnames,
                                                                             fields.parent_phone_number,
                                                                             fields.parent_additional_phone_number,
                                                                             fields.parent_email)
            if not parent:
                return result

            bank_account, result.bank_account_state, result.error = BankAccount.import_bank_account(parent, fields.bank_account_iban)
            if not bank_account:
                return result

            after_school, result.after_school_state, result.error = AfterSchool.import_after_school(fields.after_school_name)
            if not after_school:
                return result

            after_school_edition, result.edition_state, result.error = AfterSchoolEdition.import_edition(
                after_school, fields.edition_period, fields.edition_timetable, fields.edition_levels,
                fields.edition_price_for_members, fields.edition_price_for_no_members,
                Command.CREATE_EDITION_IF_NOT_EXISTS)
            if not after_school_edition:
                return result

            result.registration, result.registration_state = AfterSchoolRegistration.import_registration(
                after_school_edition, bank_account, child)

        except Exception as e:
            self.logger.error(f'Row {fields.row_index + 1}: {traceback.format_exc()}')
            result.error = str(e)

        return result
