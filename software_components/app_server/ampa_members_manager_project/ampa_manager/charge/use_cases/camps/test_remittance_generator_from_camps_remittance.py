from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.use_cases.camps.remittance_generator_from_camps_remittance import \
    RemittanceGeneratorFromCampsRemittance
from ampa_manager.tests.generator_adder import iban_generator

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestRemittanceGeneratorFromCampsRemittance(TestCase):
    def test_generate_camps_remittance_no_receipts(self):
        # Arrange
        camps_remittance: CampsRemittance = baker.make('CampsRemittance')

        # Act
        remittance: Remittance = RemittanceGeneratorFromCampsRemittance(
            camps_remittance=camps_remittance).generate()

        # Assert
        self.assertEqual(remittance.name, camps_remittance.name)
        self.assertEqual(len(remittance.receipts), 0)

    def test_generate_camps_remittance_one_receipt(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        camps_remittance: CampsRemittance = baker.make('CampsRemittance')
        baker.make('CampsReceipt', remittance=camps_remittance)

        # Act
        remittance: Remittance = RemittanceGeneratorFromCampsRemittance(
            camps_remittance=camps_remittance).generate()

        # Assert
        self.assertEqual(remittance.name, camps_remittance.name)
        self.assertEqual(len(remittance.receipts), 1)
