from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.receipt import Receipt
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.tests.generator_adder import iban_generator
from .custody_receipt import CustodyReceipt
from ..receipt_exceptions import NoSwiftBicException

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCustodyReceipt(TestCase):
    def test_generate_receipt_no_bic(self):
        # Arrange
        custody_receipt: CustodyReceipt = baker.make(CustodyReceipt)

        # Act
        with self.assertRaises(NoSwiftBicException):
            custody_receipt.generate_receipt()

    def test_generate_receipt_authorization(self):
        # Arrange
        baker.make(BankBicCode, bank_code='2095')
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        custody_receipt: CustodyReceipt = baker.make(CustodyReceipt)

        # Act
        receipt: Receipt = custody_receipt.generate_receipt()

        # Assert
        holder: Holder = custody_receipt.custody_registration.holder
        self.assertEqual(receipt.bank_account_owner, holder.parent.full_name)
        self.assertEqual(receipt.iban, holder.bank_account.iban)
        self.assertEqual(receipt.bic, holder.bank_account.swift_bic)
        self.assertEqual(receipt.authorization.number, holder.authorization_full_number)
        self.assertEqual(receipt.authorization.date, holder.authorization_sign_date)
        self.assertEqual(receipt.amount, float(custody_receipt.amount))
