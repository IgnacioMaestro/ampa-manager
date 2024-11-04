from unittest import TestCase

from model_bakery import baker

from .custody_importer import CustodyImporter
from ...models.custody.custody_edition import CustodyEdition


class TestCustodyImporter(TestCase):
    EXCEL_FILE_PATH = './ampa_manager/static/templates/plantilla_importar_ludoteca.xls'

    @classmethod
    def setUpClass(cls):
        pass

    def test_obtain_row_with_authorization(self):

        # Arrange
        edition = baker.make(CustodyEdition)
        excel_content = open(self.EXCEL_FILE_PATH, 'rb').read()

        # Act
        result = CustodyImporter(excel_content, edition).run()
