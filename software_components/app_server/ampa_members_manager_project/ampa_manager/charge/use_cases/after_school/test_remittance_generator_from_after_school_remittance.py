from typing import Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.remittance import Remittance
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.models import AfterSchoolRemittance
from ampa_manager.tests.generator_adder import bic_generator, phonenumbers_generator, iban_generator
from .remittance_generator_from_after_school_remittance import RemittanceGeneratorFromAfterSchoolRemittance
from ..remittance_creator_error import RemittanceCreatorError
from ...models.after_school_charge.after_school_receipt import AfterSchoolReceipt

baker.generators.add('localflavor.generic.models.BICField', bic_generator)
baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', phonenumbers_generator)
baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestRemittanceGeneratorFromAfterSchoolRemittance(TestCase):
    def test_generate_after_school_remittance_no_receipts(self):
        # Arrange
        after_school_remittance: AfterSchoolRemittance = baker.make(AfterSchoolRemittance)

        # Act
        remittance: Optional[Remittance]
        error: Optional[RemittanceCreatorError]
        remittance, error = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=after_school_remittance).generate()

        # Assert
        self.assertIsNone(error)
        self.assertEqual(remittance.name, after_school_remittance.name)
        self.assertEqual(remittance.created_date, after_school_remittance.created_at)
        self.assertEqual(len(remittance.receipts), 0)

    def test_generate_after_school_remittance_one_receipt_no_swift_bic(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        after_school_remittance: AfterSchoolRemittance = baker.make(AfterSchoolRemittance)
        baker.make(AfterSchoolReceipt, remittance=after_school_remittance)

        # Act
        remittance: Optional[Remittance]
        error: Optional[RemittanceCreatorError]
        remittance, error = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=after_school_remittance).generate()

        # Assert
        self.assertEqual(error, RemittanceCreatorError.BIC_ERROR)
        self.assertEqual(remittance, None)

    def test_generate_after_school_remittance_one_receipt(self):
        # Arrange
        baker.make(BankBicCode, bank_code='2095')
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        after_school_remittance: AfterSchoolRemittance = baker.make(AfterSchoolRemittance)
        baker.make(AfterSchoolReceipt, remittance=after_school_remittance)

        # Act
        remittance: Optional[Remittance]
        error: Optional[RemittanceCreatorError]
        remittance, error = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=after_school_remittance).generate()

        # Assert
        self.assertIsNone(error)
        self.assertEqual(remittance.name, after_school_remittance.name)
        self.assertEqual(remittance.created_date, after_school_remittance.created_at)
        self.assertEqual(len(remittance.receipts), 1)
