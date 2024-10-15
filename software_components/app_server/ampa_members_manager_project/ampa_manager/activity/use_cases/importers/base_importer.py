from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.child_importer import ChildImporter
from ampa_manager.family.use_cases.importers.family_importer import FamilyImporter
from ampa_manager.family.use_cases.importers.holder_importer import HolderImporter
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.utils.string_utils import StringUtils


class BaseImporter:
    KEY_FAMILY_EMAIL = 'family_email'
    KEY_FAMILY_SURNAMES = 'family_surnames'
    KEY_PARENT_NAME_AND_SURNAMES = 'parent_name_and_surnames'
    KEY_PARENT_PHONE_NUMBER = 'parent_phone_number'
    KEY_PARENT_EMAIL = 'parent_email'
    KEY_BANK_ACCOUNT_IBAN = 'bank_account_iban'
    KEY_CHILD_NAME = 'child_name'
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

    SHORT_LABEL_FAMILY_EMAIL = _('Family email')
    SHORT_LABEL_PARENT_NAME_AND_SURNAMES = _('Parent name')
    SHORT_LABEL_PARENT_PHONE_NUMBER = _('Parent phone')
    SHORT_LABEL_PARENT_EMAIL = _('Parent email')
    SHORT_LABEL_BANK_ACCOUNT_IBAN = _('IBAN')
    SHORT_LABEL_CHILD_NAME = _('Child name')
    SHORT_LABEL_CHILD_SURNAMES = _('Child surnames')
    SHORT_LABEL_CHILD_LEVEL = _('Child level')
    SHORT_LABEL_CHILD_YEAR_OF_BIRTH = _('Child year')

    @classmethod
    def import_family(cls, row: Row) -> Optional[Family]:
        family_surnames = row.get_value(cls.KEY_FAMILY_SURNAMES)
        family_email = row.get_value(cls.KEY_FAMILY_EMAIL)

        result: ImportModelResult = FamilyImporter(
            family_surnames=family_surnames,
            family_email=family_email).import_family()
        row.add_imported_model_result(result)

        return result.instance

    @classmethod
    def import_child(cls, row: Row, family: Family) -> Optional[Child]:
        name = row.get_value(cls.KEY_CHILD_NAME)
        level = row.get_value(cls.KEY_CHILD_LEVEL)
        year_of_birth = row.get_value(cls.KEY_CHILD_YEAR_OF_BIRTH)

        result: ImportModelResult = ChildImporter(
            family=family,
            name=name,
            level=level,
            year_of_birth=year_of_birth).import_child()

        row.add_imported_model_result(result)

        return result.instance

    @classmethod
    def import_parent(cls, row: Row, family: Family) -> Optional[Parent]:
        name_and_surnames = row.get_value(cls.KEY_PARENT_NAME_AND_SURNAMES)
        phone_number = row.get_value(cls.KEY_PARENT_PHONE_NUMBER)
        email = row.get_value(cls.KEY_PARENT_EMAIL)

        result: ImportModelResult = ParentImporter(
            family=family,
            name_and_surnames=name_and_surnames,
            phone_number=phone_number,
            additional_phone_number=None,
            email=email).import_parent()

        row.add_imported_model_result(result)

        return result.instance

    @classmethod
    def import_bank_account_and_holder(cls, row: Row, parent: Parent) -> Optional[Holder]:
        iban = row.get_value(cls.KEY_BANK_ACCOUNT_IBAN)

        account_result: ImportModelResult = BankAccountImporter(
            parent=parent,
            iban=iban).import_bank_account()
        row.add_imported_model_result(account_result)

        if not account_result.instance:
            return None

        holder_result: ImportModelResult = HolderImporter(
            parent=parent,
            bank_account=account_result.instance).import_holder()
        row.add_imported_model_result(holder_result)

        return holder_result.instance
