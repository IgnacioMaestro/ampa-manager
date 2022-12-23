from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_members_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.tests.generator_adder import bic_generator, phonenumbers_generator, iban_generator

baker.generators.add('localflavor.generic.models.BICField', bic_generator)
baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', phonenumbers_generator)
baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestAfterSchoolReceipt(TestCase):
    def test_generate_receipt_no_authorization(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_receipt: AfterSchoolReceipt = baker.make('AfterSchoolReceipt')

        # Act
        receipt: Receipt = after_school_receipt.generate_receipt()

        # Assert
        after_school_edition: AfterSchoolEdition = after_school_receipt.after_school_registration.after_school_edition
        self.assert_bank_account(after_school_receipt, receipt)
        self.assertEqual(receipt.authorization_number, Receipt.NO_AUTHORIZATION_MESSAGE)
        self.assertIsNone(receipt.authorization_date)
        self.assertEqual(receipt.amount, str(float(after_school_edition.price_for_no_member)))

    def test_generate_receipt_authorization(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_receipt: AfterSchoolReceipt = baker.make('AfterSchoolReceipt')
        authorization: Authorization = baker.make(
            'Authorization', bank_account=after_school_receipt.after_school_registration.bank_account)

        # Act
        receipt: Receipt = after_school_receipt.generate_receipt()

        # Assert
        after_school_edition: AfterSchoolEdition = after_school_receipt.after_school_registration.after_school_edition
        self.assert_bank_account(after_school_receipt, receipt)
        self.assertEqual(receipt.authorization_number, authorization.full_number)
        # self.assertEqual(receipt.authorization_date, authorization.date)
        self.assertEqual(receipt.amount, str(float(after_school_edition.price_for_no_member)))

    def assert_bank_account(self, after_school_receipt, receipt):
        bank_account: BankAccount = after_school_receipt.after_school_registration.bank_account
        self.assertEqual(receipt.bank_account_owner, bank_account.owner.full_name)
        self.assertEqual(receipt.iban, bank_account.iban)
