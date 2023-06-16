from typing import Optional

import pandas
from django.core.files.uploadedfile import InMemoryUploadedFile

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership


class MembershipExcelChecker:
    COLUMN_NAME_IS_MEMBER = 'FAMILIA SOCIA'
    COLUMN_NAME_FAMILY_ID = 'ID FAMILIA'
    VALUE_MEMBER = 'SI'
    VALUE_NON_MEMBER = 'NO'
    VALUE_NOT_FOUND = 'No encontrada'
    FILE_PATH = 'media/socios.xlsx'

    def __init__(self, file: InMemoryUploadedFile):
        self.dataframe = pandas.read_excel(file)
        self.set_headers()
        self.complete_membership_column()
        self.save_to_file()

    def set_headers(self):
        self.dataframe[self.COLUMN_NAME_IS_MEMBER] = self.VALUE_NON_MEMBER
        self.dataframe[self.COLUMN_NAME_FAMILY_ID] = self.VALUE_NOT_FOUND

    def complete_membership_column(self):
        for row_index in range(0, len(self.dataframe)):
            family = self.find_family(row_index)
            self.set_membership(row_index, family)

    def find_family(self, row_index) -> Optional[Family]:
        row = self.dataframe.iloc[row_index]
        family_surnames = str(row[0])
        parent1_full_name = str(row[1])
        parent2_full_name = str(row[2])
        family, _ = Family.find(family_surnames, [parent1_full_name, parent2_full_name])
        if family:
            return family
        return None

    def set_membership(self, row_index, family: Family):
        if family:
            self.dataframe.loc[row_index, self.COLUMN_NAME_FAMILY_ID] = str(family.id)

            if Membership.is_member_family(family):
                self.dataframe.loc[row_index, self.COLUMN_NAME_IS_MEMBER] = self.VALUE_MEMBER

    def save_to_file(self):
        self.dataframe.to_excel(self.FILE_PATH, index=False)

    def get_file(self):
        return open(self.FILE_PATH, "rb")
