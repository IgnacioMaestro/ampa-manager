from typing import Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.tests.generator_adder import iban_generator
from .custody_remittance_creator import CustodyRemittanceCreator
from ...remittance_creator_error import RemittanceCreatorError
from ....models.custody.custody_receipt import CustodyReceipt
from ....models.custody.custody_remittance import CustodyRemittance
from ....no_custody_edition_error import NoCustodyEditionError

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCustodyRemittanceCreator(TestCase):
    def test_create_no_after_school_edition(self):
        with self.assertRaises(NoCustodyEditionError):
            CustodyRemittanceCreator(CustodyEdition.objects.none()).create()

    def test_create_custody_edition_with_custody_registration_with_no_swift_bic(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        holder: Holder = baker.make(Holder)
        baker.make(CustodyRegistration, holder=holder)

        # Act
        custody_remittance: Optional[CustodyRemittance]
        error: Optional[RemittanceCreatorError]
        custody_remittance, error = CustodyRemittanceCreator(CustodyEdition.objects.all()).create()

        # Assert
        self.assertEqual(error, RemittanceCreatorError.BIC_ERROR)
        self.assertIsNone(custody_remittance)

    def test_create_custody_edition_with_custody_registration(self):
        # Arrange
        DynamicSetting().save()
        baker.make(BankBicCode, bank_code='2095')
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        holder: Holder = baker.make(Holder)
        custody_registration: CustodyRegistration = baker.make(CustodyRegistration, holder=holder)

        # Act
        custody_remittance: Optional[CustodyRemittance]
        error: Optional[RemittanceCreatorError]
        custody_remittance, error = CustodyRemittanceCreator(CustodyEdition.objects.all()).create()

        # Assert
        self.assertIsNotNone(custody_remittance)
        custody_receipt: CustodyReceipt = CustodyReceipt.objects.get(remittance=custody_remittance)
        self.assertAlmostEqual(custody_receipt.amount, custody_registration.calculate_price(), 2)
        self.assertIsNone(error)

    def test_create_custody_edition_with_two_custody_registrations(self):
        # Arrange
        baker.make(BankBicCode, bank_code='2095')
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        custody_edition: CustodyEdition = baker.make(CustodyEdition)
        holder: Holder = baker.make(Holder)
        baker.make(CustodyRegistration, holder=holder, custody_edition=custody_edition, _quantity=2)

        # Act
        custody_remittance: Optional[CustodyRemittance]
        error: Optional[RemittanceCreatorError]
        custody_remittance, error = CustodyRemittanceCreator(CustodyEdition.objects.all()).create()

        # Assert
        self.assertIsNotNone(custody_remittance)
        self.assertEqual(CustodyReceipt.objects.filter(remittance=custody_remittance).count(), 2)
        self.assertIsNone(error)
