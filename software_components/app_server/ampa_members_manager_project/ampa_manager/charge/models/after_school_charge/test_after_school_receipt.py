from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.family.models.authorization.authorization import Authorization
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.tests.generator_adder import bic_generator, phonenumbers_generator, iban_generator
from .after_school_receipt import AfterSchoolReceipt
from ...receipt import Receipt

baker.generators.add('localflavor.generic.models.BICField', bic_generator)
baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', phonenumbers_generator)
baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestAfterSchoolReceipt(TestCase):
    after_school_receipt: AfterSchoolReceipt

    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        cls.after_school_receipt: AfterSchoolReceipt = baker.make('AfterSchoolReceipt')

    def test_generate_receipt_no_authorization(self):
        # Act
        receipt: Receipt = self.after_school_receipt.generate_receipt()

        # Assert
        self.assert_bank_account(self.after_school_receipt, receipt)
        self.assertIsNone(receipt.authorization)
        self.assertEqual(receipt.amount, float(self.after_school_receipt.amount))

    def test_generate_receipt_authorization(self):
        # Arrange
        authorization: Authorization = baker.make(
            'Authorization', bank_account=self.after_school_receipt.after_school_registration.bank_account)

        # Act
        receipt: Receipt = self.after_school_receipt.generate_receipt()

        # Assert
        self.assert_bank_account(self.after_school_receipt, receipt)
        self.assertEqual(receipt.authorization.number, authorization.full_number)
        self.assertEqual(receipt.authorization.date, authorization.sign_date)
        self.assertEqual(receipt.amount, float(self.after_school_receipt.amount))

    def assert_bank_account(self, after_school_receipt, receipt):
        bank_account: BankAccount = after_school_receipt.after_school_registration.bank_account
        self.assertEqual(receipt.bank_account_owner, bank_account.owner.full_name)
        self.assertEqual(receipt.iban, bank_account.iban)
        self.assertEqual(receipt.bic, bank_account.swift_bic)
