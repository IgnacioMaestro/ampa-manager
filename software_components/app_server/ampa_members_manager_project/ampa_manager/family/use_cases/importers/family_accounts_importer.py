from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.excel_column_definition import ExcelColumnDefinition
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult, ModifiedField
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.bank_account_importer import BankAccountImporter
from ampa_manager.family.use_cases.importers.family_holders_consolidator import FamilyHoldersConsolidator
from ampa_manager.family.use_cases.importers.parent_importer import ParentImporter
from ampa_manager.utils.fields_formatters import FieldsFormatters


class FamilyAccountsImporter(BaseImporter):
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    KEY_FAMILY_FIRST_SURNAME = 'family_first_surname'
    KEY_FAMILY_SECOND_SURNAME = 'family_second_surname'
    KEY_HOLDER_NAME_AND_SURNAMES = 'holder_name_and_surnames'
    KEY_HOLDER_EMAIL = 'holder_email'
    KEY_HOLDER_PHONE_NUMBER = 'holder_phone_number'

    family_first_surname = ExcelColumnDefinition(
        KEY_FAMILY_FIRST_SURNAME, _('Family: first surname'), _('First surname'),
        FieldsFormatters.format_name, BaseImporter.STYLE_FAMILY)
    family_second_surname = ExcelColumnDefinition(
        KEY_FAMILY_SECOND_SURNAME, _('Family: second surname'), _('Second surname'),
        FieldsFormatters.format_name, BaseImporter.STYLE_FAMILY)
    holder_name_and_surnames = ExcelColumnDefinition(
        KEY_HOLDER_NAME_AND_SURNAMES, _('Holder: name and surnames'), _('Holder'),
        FieldsFormatters.format_name, BaseImporter.STYLE_PARENT1)
    holder_phone_number = ExcelColumnDefinition(
        KEY_HOLDER_PHONE_NUMBER, _('Holder: phone number'), _('Holder phone'),
        FieldsFormatters.format_phone, BaseImporter.STYLE_PARENT1)
    holder_email = ExcelColumnDefinition(
        KEY_HOLDER_EMAIL, _('Holder: email'), _('Holder email'),
        FieldsFormatters.format_email, BaseImporter.STYLE_PARENT1)

    COLUMNS_TO_IMPORT = [
        ExcelColumn(0, BaseImporter.family_email, compulsory=False),
        ExcelColumn(1, family_first_surname, compulsory=False),
        ExcelColumn(2, family_second_surname, compulsory=False),
        ExcelColumn(3, BaseImporter.bank_account_iban, compulsory=False),
        ExcelColumn(4, holder_name_and_surnames, compulsory=False),
        ExcelColumn(9, holder_email, compulsory=False),
        ExcelColumn(10, holder_phone_number, compulsory=False),
    ]

    def process_row(self, row: Row):
        if row.any_error or row.is_empty:
            return

        try:
            family = self.import_family_from_row(row)
            if not family or row.any_error:
                return

            parent = self.import_holder_parent(row, family)
            if row.any_error:
                return

            self.import_account_and_assign_holder(row, family, parent)
        except Exception as e:
            row.error = str(e)

    def import_family_from_row(self, row: Row) -> Optional[Family]:
        email = row.get_value(self.KEY_FAMILY_EMAIL)
        first_surname = row.get_value(self.KEY_FAMILY_FIRST_SURNAME)
        second_surname = row.get_value(self.KEY_FAMILY_SECOND_SURNAME)
        result = ImportModelResult(Family)

        try:
            if not email and not first_surname and not second_surname:
                result.set_error(_('Missing family email and surnames'))
            else:
                family, matched_by_email = self.find_family(email, first_surname, second_surname)
                if family:
                    self.update_existing_family(
                        family, result, email, first_surname, second_surname, matched_by_email)
                else:
                    self.create_family(result, email, first_surname, second_surname)
        except Exception as e:
            result.set_error(str(e))

        row.add_imported_model_result(result)
        return result.instance

    def find_family(self, email: Optional[str], first_surname: Optional[str], second_surname: Optional[str]):
        if email:
            family = Family.objects.with_this_email(email).first()
            if family:
                return family, True

        surnames = self.compose_surnames(first_surname, second_surname)
        if surnames:
            family = Family.objects.with_these_surnames(surnames).first()
            if family:
                return family, False

        return None, False

    def create_family(self, result: ImportModelResult, email: Optional[str], first_surname: Optional[str],
                      second_surname: Optional[str]):
        surnames = self.compose_surnames(first_surname, second_surname)
        if not surnames:
            result.set_error(_('Email not found, missing surnames'))
            return

        family = Family.objects.create(surnames=surnames, email=email)
        result.set_created(family)
        result.add_warning(_('Family created'))

    def update_existing_family(self, family: Family, result: ImportModelResult, email: Optional[str],
                               first_surname: Optional[str], second_surname: Optional[str], matched_by_email: bool):
        modified_fields = []

        if not matched_by_email:
            self.assign_email_without_overwriting(family, email, modified_fields, result)

        new_surnames = self.merge_surnames(family.surnames, first_surname, second_surname)
        if new_surnames and new_surnames != family.surnames:
            modified_fields.append(ModifiedField(_('Surnames'), family.surnames, new_surnames))
            family.surnames = new_surnames

        if modified_fields:
            family.save()
            result.set_updated(family, modified_fields)
        else:
            result.set_not_modified(family)

    @staticmethod
    def assign_email_without_overwriting(family: Family, email: Optional[str], modified_fields: list,
                                         result: ImportModelResult):
        if not email or family.email_matches(email):
            return

        if not family.email:
            modified_fields.append(ModifiedField(_('Email'), family.email, email))
            family.email = email
        elif not family.secondary_email:
            modified_fields.append(ModifiedField(_('Secondary email'), family.secondary_email, email))
            family.secondary_email = email
        else:
            result.add_warning(_('Family already has two different emails. Email not updated'))

    def import_holder_parent(self, row: Row, family: Family) -> Optional[Parent]:
        name_and_surnames = row.get_value(self.KEY_HOLDER_NAME_AND_SURNAMES)
        phone_number = row.get_value(self.KEY_HOLDER_PHONE_NUMBER)
        email = row.get_value(self.KEY_HOLDER_EMAIL)

        if not name_and_surnames:
            if phone_number or email:
                result = ImportModelResult(Parent)
                result.set_omitted(warning=_('Missing holder name. Parent not imported'))
                row.add_imported_model_result(result)
            return None

        result = ParentImporter(
            family=family,
            name_and_surnames=name_and_surnames,
            phone_number=phone_number,
            additional_phone_number=None,
            email=email,
            compulsory=True).import_parent()
        row.add_imported_model_result(result)
        return result.instance

    def import_account_and_assign_holder(self, row: Row, family: Family, parent: Optional[Parent]):
        iban = row.get_value(self.KEY_BANK_ACCOUNT_IBAN)
        if not iban:
            return

        if not parent:
            account_result = BankAccountImporter(parent=None, iban=iban).import_bank_account()
            if not account_result.error:
                account_result.add_warning(_('IBAN without holder name. Holder not linked'))
            row.add_imported_model_result(account_result)
            return

        previous_holder = family.membership_holder
        holder = self.import_bank_account_and_holder(row, parent)
        if not holder:
            return

        family.update_membership_holder(holder)
        if family.membership_holder_id != (previous_holder.id if previous_holder else None):
            row.add_warning_to_imported_model(_('Membership holder updated'), Family)

        FamilyHoldersConsolidator(family).consolidate()

    @staticmethod
    def compose_surnames(first_surname: Optional[str], second_surname: Optional[str]) -> Optional[str]:
        parts = [surname for surname in (first_surname, second_surname) if surname]
        if not parts:
            return None
        return ' '.join(parts)

    @staticmethod
    def split_surnames(surnames: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        if not surnames:
            return None, None
        parts = str(surnames).split(' ', 1)
        second_surname = parts[1] if len(parts) > 1 else None
        return parts[0], second_surname

    def merge_surnames(self, current_surnames: Optional[str], first_surname: Optional[str],
                       second_surname: Optional[str]) -> Optional[str]:
        if not first_surname and not second_surname:
            return current_surnames

        current_first, current_second = self.split_surnames(current_surnames)
        merged_first = first_surname or current_first
        merged_second = second_surname or current_second
        return self.compose_surnames(merged_first, merged_second)
