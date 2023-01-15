from dataclasses import dataclass
from typing import Optional


@dataclass
class RegistrationExcelRow:
    row_index: Optional[int]
    family_surnames: Optional[str]
    child_name: Optional[str]
    child_level: Optional[str]
    child_year_of_birth: Optional[int]
    parent_name_and_surnames: Optional[str]
    parent_phone_number: Optional[str]
    parent_additional_phone_number: Optional[str]
    parent_email: Optional[str]
    bank_account_iban: Optional[str]
    after_school_name: Optional[str]
    edition_timetable: Optional[str]
    edition_period: Optional[str]
    edition_levels: Optional[str]
    edition_price_for_members: Optional[int]
    edition_price_for_no_members: Optional[int]