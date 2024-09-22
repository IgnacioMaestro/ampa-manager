from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.family import Family
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.utils.excel.excel_importer import ExcelImporter
from ampa_manager.utils.excel.excel_row import ExcelRow
from ampa_manager.utils.excel.import_model_result import ImportModelResult
from ampa_manager.utils.excel.import_row_result import ImportRowResult
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.views.import_info import ImportInfo


class FamilyEmailImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 1

    KEY_FAMILY_EMAIL = 'family_email'
    KEY_FAMILY_FIRST_SURNAME = 'family_surname_1'
    KEY_FAMILY_SECOND_SURNAME = 'family_surname_2'

    LABEL_FAMILY_EMAIL = _('Family email')
    LABEL_FAMILY_FIRST_SURNAME = _('Family first surname')
    LABEL_FAMILY_SECOND_SURNAME = _('Family second surname')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.format_string, KEY_FAMILY_EMAIL, LABEL_FAMILY_EMAIL],
        [1, FieldsFormatters.format_string, KEY_FAMILY_FIRST_SURNAME, LABEL_FAMILY_FIRST_SURNAME],
        [2, FieldsFormatters.format_string, KEY_FAMILY_SECOND_SURNAME, LABEL_FAMILY_SECOND_SURNAME],
    ]

    @classmethod
    def import_family_email(cls, file_content) -> ImportInfo:
        importer = ExcelImporter(
            cls.SHEET_NUMBER, cls.FIRST_ROW_INDEX, cls.COLUMNS_TO_IMPORT, file_content=file_content)

        importer.counters_before = cls.count_objects()

        for row in importer.get_rows():
            result = cls.process_row(row)
            importer.add_result(result)

        importer.counters_after = cls.count_objects()

        return ImportInfo(
            importer.total_rows, importer.successfully_imported_rows, importer.get_summary(), importer.get_results())

    @classmethod
    def count_objects(cls):
        return {
            Family.__name__: Family.objects.count(),
        }

    @classmethod
    def process_row(cls, row: ExcelRow) -> ImportRowResult:
        result = ImportRowResult(row)

        if row.error:
            result.error = row.error
            return result

        try:
            family_surnames = f'{row.get(cls.KEY_FAMILY_FIRST_SURNAME)} {row.get(cls.KEY_FAMILY_SECOND_SURNAME)}'
            email = row.get(cls.KEY_FAMILY_EMAIL)
            family_result: ImportModelResult = FamilyImporter.import_family(family_surnames=family_surnames,
                                                                            family_email=email)
            result.add_partial_result(family_result)

        except Exception as e:
            result.error = str(e)

        return result
