from typing import Optional
from unittest import TestCase

from ampa_manager.academic_course.models.level_constants import LevelConstants
from ..excel_extracted_types.child_import_data import ChildImportData
from ..excel_extracted_types.child_with_surnames_import_data import ChildWithSurnamesImportData
from ..excel_extracted_types.holder_import_data import HolderImportData
from ..excel_extracted_types.parent_import_data import ParentImportData
from ..rows_importer.custody_child_import_data import CustodyChildImportData


class TestRowImporterAsserts(TestCase):
    def assert_holder(self, holder_import_data: Optional[HolderImportData]):
        self.assertIsNotNone(holder_import_data)
        self.assertEqual(holder_import_data.iban, 'ES3731908578142288961735')
        parent_import_data: ParentImportData = holder_import_data.parent_import_data
        self.assertIsNotNone(parent_import_data)
        self.assertEqual(parent_import_data.holder_name_and_surnames, 'Padre Lopez Perez')
        self.assertEqual(parent_import_data.phone_number, '+34600500400')
        self.assertEqual(parent_import_data.email, 'padre@gmail.com')

    def assert_child(self, custody_child_import_data: CustodyChildImportData):
        self.assertEqual(custody_child_import_data.days_attended, 17)
        child_with_surnames_import_data: ChildWithSurnamesImportData = custody_child_import_data.child_with_surnames_import_data
        self.assertEqual(child_with_surnames_import_data.surnames, 'Lopez Gonzalez')
        child_import_data: ChildImportData = child_with_surnames_import_data.child_import_data
        self.assertEqual(child_import_data.name, 'Nahia')
        self.assertEqual(child_import_data.level, LevelConstants.ID_LH4)
        self.assertEqual(child_import_data.birth_year, 2013)
