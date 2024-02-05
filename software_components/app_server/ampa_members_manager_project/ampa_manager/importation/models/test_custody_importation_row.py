from django.test import TestCase
from model_bakery import baker

from ampa_manager.importation.models.custody_importation_row import CustodyImportationRow


class TestCustodyImportationRow(TestCase):

    def test_custody_importation_row_str(self):
        custody_importation_row: CustodyImportationRow = baker.prepare(
            'CustodyImportationRow', iban='ES9121000418450200051332')

        custody_importation_row_str = str(custody_importation_row)

        expected_str = custody_importation_row.name + ' - ' + custody_importation_row.surnames
        self.assertEqual(custody_importation_row_str, expected_str)
