from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.use_cases.custody.remittance_generator_from_custody_remittance import \
    RemittanceGeneratorFromCustodyRemittance
from ampa_manager.tests.generator_adder import iban_generator

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestRemittanceGeneratorFromCustodyRemittance(TestCase):
    def test_generate_custody_remittance_no_receipts(self):
        # Arrange
        custody_remittance: CustodyRemittance = baker.make('CustodyRemittance')

        # Act
        remittance: Remittance = RemittanceGeneratorFromCustodyRemittance(
            custody_remittance=custody_remittance).generate()

        # Assert
        self.assertEqual(remittance.name, custody_remittance.name)
        self.assertEqual(len(remittance.receipts), 0)

    def test_generate_custody_remittance_one_receipt(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        custody_remittance: CustodyRemittance = baker.make('CustodyRemittance')
        baker.make('CustodyReceipt', remittance=custody_remittance)

        # Act
        remittance: Remittance = RemittanceGeneratorFromCustodyRemittance(
            custody_remittance=custody_remittance).generate()

        # Assert
        self.assertEqual(remittance.name, custody_remittance.name)
        self.assertEqual(len(remittance.receipts), 1)
