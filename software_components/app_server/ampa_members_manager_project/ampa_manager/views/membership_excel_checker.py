import pandas
from django.core.files.uploadedfile import InMemoryUploadedFile

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership


class MembershipExcelChecker:
    MEMBERS_COLUMN_NAME = 'FAMILIA SOCIA'
    VALUE_MEMBER = 'SI'
    VALUE_NON_MEMBER = 'NO'
    FILE_PATH = 'media/socios.xlsx'

    def __init__(self, file: InMemoryUploadedFile):
        self.dataframe = pandas.read_excel(file)
        self.set_members_header()
        self.complete_membership_column()
        self.save_to_file()

    def set_members_header(self):
        self.dataframe[self.MEMBERS_COLUMN_NAME] = self.VALUE_NON_MEMBER

    def complete_membership_column(self):
        for row_index in range(0, len(self.dataframe)):
            is_member = self.check_is_member(row_index)
            self.set_membership(row_index, is_member)

    def check_is_member(self, row_index) -> bool:
        row = self.dataframe.iloc[row_index]
        family_surnames = str(row[0])
        parent1_full_name = str(row[1])
        parent2_full_name = str(row[2])
        family, error = Family.find(family_surnames, [parent1_full_name, parent2_full_name])
        if family:
            return Membership.is_member_family(family)
        return False

    def set_membership(self, row_index, is_member):
        if is_member:
            self.dataframe.loc[row_index, self.MEMBERS_COLUMN_NAME] = self.VALUE_MEMBER

    def save_to_file(self):
        self.dataframe.to_excel(self.FILE_PATH, index=False)

    def get_file(self):
        return open(self.FILE_PATH, "rb")
