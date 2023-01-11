from dataclasses import dataclass
from typing import Optional


@dataclass
class MemberExcelRow:

    row_index: Optional[int]
    family_surnames: Optional[str]
    child1_name: Optional[str]
    child1_level: Optional[str]
    child1_year_of_birth: Optional[int]
    child2_name: Optional[str]
    child2_level: Optional[str]
    child2_year_of_birth: Optional[int]
    child3_name: Optional[str]
    child3_level: Optional[str]
    child3_year_of_birth: Optional[int]
    child4_name: Optional[str]
    child4_level: Optional[str]
    child4_year_of_birth: Optional[int]
    child5_name: Optional[str]
    child5_level: Optional[str]
    child5_year_of_birth: Optional[int]
    parent1_name_and_surnames: Optional[str]
    parent1_phone_number: Optional[str]
    parent1_additional_phone_number: Optional[str]
    parent1_email: Optional[str]
    parent2_name_and_surnames: Optional[str]
    parent2_phone_number: Optional[str]
    parent2_additional_phone_number: Optional[str]
    parent2_email: Optional[str]
    parent1_bank_account_iban: Optional[str]
    parent1_bank_account_swift_bic: Optional[str]
    parent1_bank_account_is_default: Optional[bool]
    parent2_bank_account_iban: Optional[str]
    parent2_bank_account_swift_bic: Optional[str]
    parent2_bank_account_is_default: Optional[bool]

    def child1_has_data(self):
        return self.child1_name or self.child1_level or self.child1_year_of_birth

    def child2_has_data(self):
        return self.child2_name or self.child2_level or self.child2_year_of_birth

    def child3_has_data(self):
        return self.child3_name or self.child3_level or self.child3_year_of_birth

    def child4_has_data(self):
        return self.child4_name or self.child4_level or self.child4_year_of_birth

    def child5_has_data(self):
        return self.child5_name or self.child5_level or self.child5_year_of_birth

    def parent1_has_data(self):
        return self.parent1_name_and_surnames or self.parent1_phone_number or self.parent1_additional_phone_number or self.parent1_email

    def parent2_has_data(self):
        return self.parent2_name_and_surnames or self.parent2_phone_number or self.parent2_additional_phone_number or self.parent2_email

    def parent1_bank_account_has_data(self):
        return self.parent1_bank_account_iban or self.parent1_bank_account_swift_bic or self.parent1_bank_account_is_default

    def parent2_bank_account_has_data(self):
        return self.parent2_bank_account_iban or self.parent2_bank_account_swift_bic or self.parent2_bank_account_is_default