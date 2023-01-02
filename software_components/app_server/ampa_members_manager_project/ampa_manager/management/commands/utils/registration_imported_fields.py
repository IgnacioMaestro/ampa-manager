class RegistrationImportedFields:

    def __init__(self, family_surnames, child_name, child_level, child_year_of_birth, parent_name_and_surnames,
                 parent_phone_number, parent_additional_phone_number, parent_email, bank_account_iban,
                 after_school_name, edition_timetable, edition_period, edition_price_for_members,
                 edition_price_for_no_members, edition_levels):

        self.family_surnames = family_surnames
        self.child_name = child_name
        self.child_level = child_level
        self.child_year_of_birth = child_year_of_birth
        self.parent_name_and_surnames = parent_name_and_surnames
        self.parent_phone_number = parent_phone_number
        self.parent_additional_phone_number = parent_additional_phone_number
        self.parent_email = parent_email
        self.bank_account_iban = bank_account_iban
        self.after_school_name = after_school_name
        self.edition_timetable = edition_timetable
        self.edition_period = edition_period
        self.edition_price_for_members = edition_price_for_members
        self.edition_price_for_no_members = edition_price_for_no_members
        self.edition_levels = edition_levels

    def print(self):
        print(f' - family_surnames: {self.family_surnames} ({type(self.family_surnames)})')
        print(f' - child_name: {self.child_name} ({type(self.child_name)})')
        print(f' - child_level: {self.child_level} ({type(self.child_level)})')
        print(f' - child_year_of_birth: {self.child_year_of_birth} ({type(self.child_year_of_birth)})')
        print(f' - parent_name_and_surnames: {self.parent_name_and_surnames} ({type(self.parent_name_and_surnames)})')
        print(f' - parent_phone_number: {self.parent_phone_number} ({type(self.parent_phone_number)})')
        print(f' - parent_additional_phone_number: {self.parent_additional_phone_number} ({type(self.parent_additional_phone_number)})')
        print(f' - parent_email: {self.parent_email} ({type(self.parent_email)})')
        print(f' - bank_account_iban: {self.bank_account_iban} ({type(self.bank_account_iban)})')
        print(f' - after_school_name: {self.after_school_name} ({type(self.after_school_name)})')
        print(f' - edition_timetable: {self.edition_timetable} ({type(self.edition_timetable)})')
        print(f' - edition_period: {self.edition_period} ({type(self.edition_period)})')
        print(f' - edition_price_for_members: {self.edition_price_for_members} ({type(self.edition_price_for_members)})')
        print(f' - edition_price_for_no_members: {self.edition_price_for_no_members} ({type(self.edition_price_for_no_members)})')
        print(f' - edition_levels: {self.edition_levels} ({type(self.edition_levels)})')

    def get_list(self):
        return [self.family_surnames, self.child_name, self.child_level, self.child_year_of_birth,
                self.parent_name_and_surnames, self.parent_phone_number, self.parent_additional_phone_number,
                self.parent_email, self.bank_account_iban, self.after_school_name, self.edition_timetable,
                self.edition_period, self.edition_price_for_members, self.edition_price_for_no_members, self.edition_levels]
