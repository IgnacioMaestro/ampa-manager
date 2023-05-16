from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.remittance import Remittance
from ampa_manager.models import AfterSchoolRemittance
from ampa_manager.tests.generator_adder import bic_generator, phonenumbers_generator, iban_generator
from .remittance_generator_from_after_school_remittance import RemittanceGeneratorFromAfterSchoolRemittance

baker.generators.add('localflavor.generic.models.BICField', bic_generator)
baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', phonenumbers_generator)
baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestRemittanceGeneratorFromAfterSchoolRemittance(TestCase):
    def test_generate_after_school_remittance_no_receipts(self):
        # Arrange
        after_school_remittance: AfterSchoolRemittance = baker.make('AfterSchoolRemittance')

        # Act
        remittance: Remittance = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=after_school_remittance).generate()

        # Assert
        self.assertEqual(remittance.name, after_school_remittance.name)
        self.assertEqual(remittance.created_date, after_school_remittance.created_at)
        self.assertEqual(len(remittance.receipts), 0)

    def test_generate_after_school_remittance_one_receipt(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_remittance: AfterSchoolRemittance = baker.make('AfterSchoolRemittance')
        baker.make('AfterSchoolReceipt', remittance=after_school_remittance)

        # Act
        remittance: Remittance = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=after_school_remittance).generate()

        # Assert
        self.assertEqual(remittance.name, after_school_remittance.name)
        self.assertEqual(remittance.created_date, after_school_remittance.created_at)
        self.assertEqual(len(remittance.receipts), 1)
