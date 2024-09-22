from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.utils.excel.import_model_result import ImportModelResult
from ampa_manager.utils.string_utils import StringUtils


class BaseImporter:
    KEY_FAMILY_EMAIL = 'family_email'
    KEY_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    KEY_PARENT_PHONE_NUMBER = 'parent_phone_number'
    KEY_PARENT_EMAIL = 'parent_email'
    KEY_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    KEY_CHILD_NAME = 'child_name'
    KEY_CHILD_SURNAMES = 'child_surnames'
    KEY_CHILD_LEVEL = 'child_level'
    KEY_CHILD_YEAR_OF_BIRTH = 'child_year_of_birth'
    KEY_ASSISTED_DAYS = 'assisted_days'

    LABEL_FAMILY_EMAIL = _('Family email')
    LABEL_PARENT_NAME_AND_SURNAMES = _('Parent name and surnames')
    LABEL_PARENT_PHONE_NUMBER = _('Parent phone number')
    LABEL_PARENT_EMAIL = _('Parent email')
    LABEL_BANK_ACCOUNT_IBAN = _('Parent bank account IBAN')
    LABEL_CHILD_NAME = _('Child name (without surnames)')
    LABEL_CHILD_SURNAMES = _('Child surnames')
    LABEL_CHILD_LEVEL = _('Child level (ex. HH4, LH3)')
    LABEL_CHILD_YEAR_OF_BIRTH = _('Child year of birth (ex. 2015)')

    @classmethod
    def import_family(cls, row: Row) -> Family:
        family_surnames = row.get_value(cls.KEY_CHILD_SURNAMES)
        parent1_name_and_surnames = row.get_value(cls.KEY_PARENT_NAME_AND_SURNAMES)
        child_name = row.get_value(cls.KEY_CHILD_NAME)
        email = row.get_value(cls.KEY_FAMILY_EMAIL)

        imported_model: ImportModelResult = FamilyImporter.import_family(
            family_surnames=family_surnames,
            parent1_name_and_surnames=parent1_name_and_surnames,
            child_name=child_name,
            email=email)
        row.add_imported_model(imported_model)

        return imported_model.imported_object

    @classmethod
    def import_child(cls, row: Row, family: Family) -> Child:
        name = row.get_value(cls.KEY_CHILD_NAME)
        level = row.get_value(cls.KEY_CHILD_LEVEL)
        year_of_birth = row.get_value(cls.KEY_CHILD_YEAR_OF_BIRTH)

        imported_model: ImportModelResult = ChildImporter.import_child(
            family=family,
            name=name,
            level=level,
            year_of_birth=year_of_birth)

        row.add_imported_model(imported_model)

        return imported_model.imported_object

    @classmethod
    def import_parent(cls, row: Row, family: Family) -> Parent:
        name_and_surnames = row.get_value(cls.KEY_PARENT_NAME_AND_SURNAMES)
        phone_number = row.get_value(cls.KEY_PARENT_PHONE_NUMBER)
        email = row.get_value(cls.KEY_PARENT_EMAIL)

        imported_model: ImportModelResult = ParentImporter.import_parent(
            family=family,
            name_and_surnames=name_and_surnames,
            phone_number=phone_number,
            additional_phone_number=None,
            email=email,
            optional=True)

        row.add_imported_model(imported_model)

        return imported_model.imported_object

    @classmethod
    def import_bank_account_and_holder(cls, row: Row, parent: Parent) -> Holder:
        iban = row.get_value(cls.KEY_BANK_ACCOUNT_IBAN)

        bank_account_result, holder_result = BankAccountImporter.import_bank_account_and_holder(
            parent=parent,
            iban=iban)
        row.add_imported_model(bank_account_result)
        row.add_imported_model(holder_result)

        return holder_result.imported_object

    @classmethod
    def consolidate_family_holders(cls, family: Family):
        if not family.custody_holder:
            family.custody_holder = cls.get_last_custody_registration_holder(family)
        if not family.after_school_holder:
            family.after_school_holder = cls.get_last_after_school_registration_holder(family)
        if not family.camps_holder:
            family.camps_holder = cls.get_last_camps_registration_holder(family)

        if not family.membership_holder:
            family.membership_holder = family.get_default_holder()

        if not family.custody_holder:
            family.custody_holder = family.membership_holder
        if not family.after_school_holder:
            family.after_school_holder = family.membership_holder
        if not family.camps_holder:
            family.camps_holder = family.membership_holder

    @classmethod
    def get_last_custody_registration_holder(cls, family: Family):
        registrations = CustodyRegistration.objects.of_family(family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None

    @classmethod
    def get_last_after_school_registration_holder(cls, family: Family):
        registrations = AfterSchoolRegistration.objects.of_family(family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None

    @classmethod
    def get_last_camps_registration_holder(cls, family: Family):
        registrations = CampsRegistration.objects.of_family(family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None

    @classmethod
    def get_excel_columns(cls, columns_to_import):
        columns = []
        for column in columns_to_import:
            index = column[0]
            letter = StringUtils.get_excel_column_letter(index).upper()
            label = column[3]
            columns.append([letter, label])
        return columns
