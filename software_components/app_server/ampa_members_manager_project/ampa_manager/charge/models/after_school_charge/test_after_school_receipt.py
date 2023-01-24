from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.family.models.holder.holder import Holder
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

    def test_generate_receipt_authorization(self):
        # Act
        receipt: Receipt = self.after_school_receipt.generate_receipt()

        # Assert
        holder: Holder = self.after_school_receipt.after_school_registration.holder
        self.assertEqual(receipt.bank_account_owner, holder.parent.full_name)
        self.assertEqual(receipt.iban, holder.bank_account.iban)
        self.assertEqual(receipt.bic, holder.bank_account.swift_bic)
        self.assertEqual(receipt.authorization.number, holder.authorization_full_number)
        self.assertEqual(receipt.authorization.date, holder.authorization_sign_date)
        self.assertEqual(receipt.amount, float(self.after_school_receipt.amount))
