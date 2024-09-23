from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.old_importers.excel.excel_importer import ExcelImporter
from ampa_manager.activity.use_cases.old_importers.excel.excel_row import ExcelRow
from ampa_manager.activity.use_cases.old_importers.excel.import_row_result import ImportRowResult
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.views.import_info import ImportInfo


class MembersImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    KEY_FAMILY_SURNAMES = 'family_surnames'
    KEY_PARENT1_NAME_AND_SURNAMES = 'parent1_name_and_surnames'
    KEY_PARENT1_PHONE_NUMBER = 'parent1_phone_number'
    KEY_PARENT1_EMAIL = 'parent1_email'
    KEY_PARENT1_BANK_ACCOUNT_IBAN = 'parent1_bank_account_iban'
    KEY_PARENT2_NAME_AND_SURNAMES = 'parent2_name_and_surnames'
    KEY_PARENT2_PHONE_NUMBER = 'parent2_phone_number'
    KEY_PARENT2_EMAIL = 'parent2_email'
    KEY_CHILD1_NAME = 'child1_name'
    KEY_CHILD1_LEVEL = 'child1_level'
    KEY_CHILD1_YEAR_OF_BIRTH = 'child1_year_of_birth'
    KEY_CHILD2_NAME = 'child2_name'
    KEY_CHILD2_LEVEL = 'child2_level'
    KEY_CHILD2_YEAR_OF_BIRTH = 'child2_year_of_birth'
    KEY_CHILD3_NAME = 'child3_name'
    KEY_CHILD3_LEVEL = 'child3_level'
    KEY_CHILD3_YEAR_OF_BIRTH = 'child3_year_of_birth'
    KEY_CHILD4_NAME = 'child4_name'
    KEY_CHILD4_LEVEL = 'child4_level'
    KEY_CHILD4_YEAR_OF_BIRTH = 'child4_year_of_birth'
    KEY_CHILD5_NAME = 'child5_name'
    KEY_CHILD5_LEVEL = 'child5_level'
    KEY_CHILD5_YEAR_OF_BIRTH = 'child5_year_of_birth'

    FAMILY_FIELDS = [KEY_FAMILY_SURNAMES]
    PARENT1_FIELDS = [
        KEY_PARENT1_NAME_AND_SURNAMES,
        KEY_PARENT1_PHONE_NUMBER,
        KEY_PARENT1_EMAIL,
    ]
    PARENT2_FIELDS = [
        KEY_PARENT2_NAME_AND_SURNAMES,
        KEY_PARENT2_PHONE_NUMBER,
        KEY_PARENT2_PHONE_NUMBER,
    ]
    CHILD1_FIELDS = [
        KEY_CHILD1_NAME,
        KEY_CHILD1_LEVEL,
        KEY_CHILD1_YEAR_OF_BIRTH
    ]
    CHILD2_FIELDS = [
        KEY_CHILD2_NAME,
        KEY_CHILD2_LEVEL,
        KEY_CHILD2_YEAR_OF_BIRTH
    ]
    CHILD3_FIELDS = [
        KEY_CHILD3_NAME,
        KEY_CHILD3_LEVEL,
        KEY_CHILD3_YEAR_OF_BIRTH
    ]
    CHILD4_FIELDS = [
        KEY_CHILD4_NAME,
        KEY_CHILD4_LEVEL,
        KEY_CHILD4_YEAR_OF_BIRTH
    ]
    CHILD5_FIELDS = [
        KEY_CHILD5_NAME,
        KEY_CHILD5_LEVEL,
        KEY_CHILD5_YEAR_OF_BIRTH
    ]
    PARENT1_BANK_ACCOUNT_FIELDS = [
        KEY_PARENT1_BANK_ACCOUNT_IBAN,
    ]

    LABEL_FAMILY_SURNAMES = _('Family') + ': ' + _('Surnames')
    LABEL_PARENT1_NAME_AND_SURNAMES = _('Parent %(number)s') % {'number': 1} + ': ' + _('Name and surnames')
    LABEL_PARENT1_PHONE_NUMBER = _('Parent %(number)s') % {'number': 1} + ': ' + _('Phone number')
    LABEL_PARENT1_EMAIL = _('Parent %(number)s') % {'number': 1} + ': ' + _('Email')
    LABEL_PARENT1_BANK_ACCOUNT_IBAN = _('Parent %(number)s') % {'number': 1} + ': ' + _('Bank account IBAN')
    LABEL_PARENT2_NAME_AND_SURNAMES = _('Parent %(number)s') % {'number': 2} + ': ' + _('Name and surnames')
    LABEL_PARENT2_PHONE_NUMBER = _('Parent %(number)s') % {'number': 2} + ': ' + _('Phone number')
    LABEL_PARENT2_EMAIL = _('Parent %(number)s') % {'number': 2} + ': ' + _('Email')
    LABEL_CHILD1_NAME = _('Child %(number)s') % {'number': 1} + ': ' + _('Name (without surnames)')
    LABEL_CHILD1_LEVEL = _('Child %(number)s') % {'number': 1} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD1_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 1} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD2_NAME = _('Child %(number)s') % {'number': 2} + ': ' + _('Name (without surnames)')
    LABEL_CHILD2_LEVEL = _('Child %(number)s') % {'number': 2} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD2_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 2} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD3_NAME = _('Child %(number)s') % {'number': 3} + ': ' + _('Name (without surnames)')
    LABEL_CHILD3_LEVEL = _('Child %(number)s') % {'number': 3} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD3_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 3} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD4_NAME = _('Child %(number)s') % {'number': 4} + ': ' + _('Name (without surnames)')
    LABEL_CHILD4_LEVEL = _('Child %(number)s') % {'number': 4} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD4_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 4} + ': ' + _('Year of birth (ex. 2015)')
    LABEL_CHILD5_NAME = _('Child %(number)s') % {'number': 5} + ': ' + _('Name (without surnames)')
    LABEL_CHILD5_LEVEL = _('Child %(number)s') % {'number': 5} + ': ' + _('Level (ex. HH4, LH3)')
    LABEL_CHILD5_YEAR_OF_BIRTH = _('Child %(number)s') % {'number': 5} + ': ' + _('Year of birth (ex. 2015)')

    COLUMNS_TO_IMPORT = [
        [0, FieldsFormatters.format_name, KEY_FAMILY_SURNAMES, LABEL_FAMILY_SURNAMES],
        [1, FieldsFormatters.format_name, KEY_PARENT1_NAME_AND_SURNAMES, LABEL_PARENT1_NAME_AND_SURNAMES],
        [2, FieldsFormatters.format_phone, KEY_PARENT1_PHONE_NUMBER, LABEL_PARENT1_PHONE_NUMBER],
        [3, FieldsFormatters.format_email, KEY_PARENT1_EMAIL, LABEL_PARENT1_EMAIL],
        [4, FieldsFormatters.format_iban, KEY_PARENT1_BANK_ACCOUNT_IBAN, LABEL_PARENT1_BANK_ACCOUNT_IBAN],
        [5, FieldsFormatters.format_name, KEY_PARENT2_NAME_AND_SURNAMES, LABEL_PARENT2_NAME_AND_SURNAMES],
        [6, FieldsFormatters.format_phone, KEY_PARENT2_PHONE_NUMBER, LABEL_PARENT2_PHONE_NUMBER],
        [7, FieldsFormatters.format_email, KEY_PARENT2_EMAIL, LABEL_PARENT2_EMAIL],
        [8, FieldsFormatters.format_name, KEY_CHILD1_NAME, LABEL_CHILD1_NAME],
        [9, FieldsFormatters.format_integer, KEY_CHILD1_YEAR_OF_BIRTH, LABEL_CHILD1_YEAR_OF_BIRTH],
        [10, FieldsFormatters.format_level, KEY_CHILD1_LEVEL, LABEL_CHILD1_LEVEL],
        [11, FieldsFormatters.format_name, KEY_CHILD2_NAME, LABEL_CHILD2_NAME],
        [12, FieldsFormatters.format_integer, KEY_CHILD2_YEAR_OF_BIRTH, LABEL_CHILD2_YEAR_OF_BIRTH],
        [13, FieldsFormatters.format_level, KEY_CHILD2_LEVEL, LABEL_CHILD2_LEVEL],
        [14, FieldsFormatters.format_name, KEY_CHILD3_NAME, LABEL_CHILD3_NAME],
        [15, FieldsFormatters.format_integer, KEY_CHILD3_YEAR_OF_BIRTH, LABEL_CHILD3_YEAR_OF_BIRTH],
        [16, FieldsFormatters.format_level, KEY_CHILD3_LEVEL, LABEL_CHILD3_LEVEL],
        [17, FieldsFormatters.format_name, KEY_CHILD4_NAME, LABEL_CHILD4_NAME],
        [18, FieldsFormatters.format_integer, KEY_CHILD4_YEAR_OF_BIRTH, LABEL_CHILD4_YEAR_OF_BIRTH],
        [19, FieldsFormatters.format_level, KEY_CHILD4_LEVEL, LABEL_CHILD4_LEVEL],
        [20, FieldsFormatters.format_name, KEY_CHILD5_NAME, LABEL_CHILD5_NAME],
        [21, FieldsFormatters.format_integer, KEY_CHILD5_YEAR_OF_BIRTH, LABEL_CHILD5_YEAR_OF_BIRTH],
        [22, FieldsFormatters.format_level, KEY_CHILD5_LEVEL, LABEL_CHILD5_LEVEL],
    ]

    @classmethod
    def import_members(cls, file_content) -> ImportInfo:
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
            Parent.__name__: Parent.objects.count(),
            Child.__name__: Child.objects.count(),
            BankAccount.__name__: BankAccount.objects.count(),
            Holder.__name__: Holder.objects.count(),
            Membership.__name__: Membership.objects.count(),
        }

    @classmethod
    def process_row(cls, row: ExcelRow) -> ImportRowResult:
        result = ImportRowResult(row)

        if row.error:
            result.error = row.error
            return result

        try:
            family_result = FamilyImporter.import_family(
                row.get(cls.KEY_FAMILY_SURNAMES),
                row.get(cls.KEY_PARENT1_NAME_AND_SURNAMES),
                row.get(cls.KEY_PARENT2_NAME_AND_SURNAMES))
            result.add_partial_result(family_result)
            if not family_result.success:
                return result
            family = family_result.imported_object

            if family:
                result = cls.import_children(row, family, result)
                result = cls.import_parents(row, family, result)
                result = cls.import_membership(family, result)

        except Exception as e:
            result.error = str(e)

        return result

    @classmethod
    def import_children(cls, row: ExcelRow, family, result: ImportRowResult):

        if row.any_column_has_value(cls.CHILD1_FIELDS):
            child1_result = ChildImporter.import_child(
                family,
                row.get(cls.KEY_CHILD1_NAME),
                row.get(cls.KEY_CHILD1_LEVEL),
                row.get(cls.KEY_CHILD1_YEAR_OF_BIRTH))
            result.add_partial_result(child1_result)
            if not child1_result.success:
                return result

        if row.any_column_has_value(cls.CHILD2_FIELDS):
            child2_result = ChildImporter.import_child(
                family,
                row.get(cls.KEY_CHILD2_NAME),
                row.get(cls.KEY_CHILD2_LEVEL),
                row.get(cls.KEY_CHILD2_YEAR_OF_BIRTH))
            result.add_partial_result(child2_result)
            if not child2_result.success:
                return result

        if row.any_column_has_value(cls.CHILD3_FIELDS):
            child3_result = ChildImporter.import_child(
                family,
                row.get(cls.KEY_CHILD3_NAME),
                row.get(cls.KEY_CHILD3_LEVEL),
                row.get(cls.KEY_CHILD3_YEAR_OF_BIRTH))
            result.add_partial_result(child3_result)
            if not child3_result.success:
                return result

        if row.any_column_has_value(cls.CHILD4_FIELDS):
            child4_result = ChildImporter.import_child(
                family,
                row.get(cls.KEY_CHILD4_NAME),
                row.get(cls.KEY_CHILD4_LEVEL),
                row.get(cls.KEY_CHILD4_YEAR_OF_BIRTH))
            result.add_partial_result(child4_result)
            if not child4_result.success:
                return result

        if row.any_column_has_value(cls.CHILD5_FIELDS):
            child5_result = ChildImporter.import_child(
                family,
                row.get(cls.KEY_CHILD5_NAME),
                row.get(cls.KEY_CHILD5_LEVEL),
                row.get(cls.KEY_CHILD5_YEAR_OF_BIRTH))
            result.add_partial_result(child5_result)
            if not child5_result.success:
                return result

        return result

    @classmethod
    def import_parents(cls, row: ExcelRow, family, result: ImportRowResult):
        if row.any_column_has_value(cls.PARENT1_FIELDS):
            parent1_result = ParentImporter.import_parent(
                family,
                row.get(cls.KEY_PARENT1_NAME_AND_SURNAMES),
                row.get(cls.KEY_PARENT1_PHONE_NUMBER),
                None,
                row.get(cls.KEY_PARENT1_EMAIL))
            result.add_partial_result(parent1_result)
            if not parent1_result.success:
                return result
            parent1 = parent1_result.imported_object

            if row.any_column_has_value(cls.PARENT1_BANK_ACCOUNT_FIELDS):
                bank_account_result, holder_result = BankAccountImporter.import_bank_account_and_holder(
                    parent1,
                    row.get(cls.KEY_PARENT1_BANK_ACCOUNT_IBAN))
                result.add_partial_result(bank_account_result)
                result.add_partial_result(holder_result)

                if not bank_account_result.success or not holder_result.success:
                    return result

        if row.any_column_has_value(cls.PARENT2_FIELDS):
            parent2_result = ParentImporter.import_parent(
                family,
                row.get(cls.KEY_PARENT2_NAME_AND_SURNAMES),
                row.get(cls.KEY_PARENT2_PHONE_NUMBER),
                None,
                row.get(cls.KEY_PARENT2_EMAIL))
            result.add_partial_result(parent2_result)
            if not parent2_result.success:
                return result

        return result

    @staticmethod
    def import_membership(family, result: ImportRowResult):
        membership_result = ImportModelResult(Membership.__name__, [])

        if Membership.is_member_family(family):
            membership_result.set_not_modified(Membership.get_membership(family))
        else:
            Membership.make_member_for_active_course(family)
            membership_result.set_created(Membership.get_membership(family))

        result.add_partial_result(membership_result)

        return result
