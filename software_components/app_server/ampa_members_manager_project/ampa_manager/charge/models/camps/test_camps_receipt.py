from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.receipt import Receipt
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.tests.generator_adder import iban_generator
from .camps_receipt import CampsReceipt
from ..receipt_exceptions import NoSwiftBicException

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCampsReceipt(TestCase):
    def test_generate_receipt_no_bic(self):
        # Arrange
        camps_receipt: CampsReceipt = baker.make(CampsReceipt)

        # Act
        with self.assertRaises(NoSwiftBicException):
            camps_receipt.generate_receipt()

    def test_generate_receipt_authorization(self):
        # Arrange
        baker.make(BankBicCode, bank_code='2095')
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        camps_receipt: CampsReceipt = baker.make(CampsReceipt)

        # Act
        receipt: Receipt = camps_receipt.generate_receipt()

        # Assert
        holder: Holder = camps_receipt.camps_registration.holder
        self.assertEqual(receipt.bank_account_owner, holder.parent.full_name)
        self.assertEqual(receipt.iban, holder.bank_account.iban)
        self.assertEqual(receipt.bic, holder.bank_account.swift_bic)
        self.assertEqual(receipt.authorization.number, holder.authorization_full_number)
        self.assertEqual(receipt.authorization.date, holder.authorization_sign_date)
        self.assertEqual(receipt.amount, float(camps_receipt.amount))

