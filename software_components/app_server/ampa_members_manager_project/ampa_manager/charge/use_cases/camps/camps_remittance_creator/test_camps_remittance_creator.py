from typing import Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.tests.generator_adder import iban_generator
from .camps_remittance_creator import CampsRemittanceCreator
from ...remittance_creator_error import RemittanceCreatorError
from ....models.camps.camps_receipt import CampsReceipt
from ....models.camps.camps_remittance import CampsRemittance
from ....no_camps_edition_error import NoCampsEditionError

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCampsRemittanceCreator(TestCase):
    def test_create_no_after_school_edition(self):
        with self.assertRaises(NoCampsEditionError):
            CampsRemittanceCreator(CampsEdition.objects.none()).create()

    def test_create_camps_remittance_with_no_swift_bic(self):
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        holder: Holder = baker.make(Holder)
        baker.make(CampsRegistration, holder=holder)

        camps_remittance: Optional[CampsRemittance]
        error: Optional[RemittanceCreatorError]
        camps_remittance, error = CampsRemittanceCreator(CampsEdition.objects.all()).create()

        self.assertEqual(error, RemittanceCreatorError.BIC_ERROR)
        self.assertIsNone(camps_remittance)

    def test_create_camps_remittance_with_camps_registration(self):
        baker.make(BankBicCode, bank_code='2095')
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        holder: Holder = baker.make(Holder)
        camps_registration: CampsRegistration = baker.make(CampsRegistration, holder=holder)

        camps_remittance: Optional[CampsRemittance]
        error: Optional[RemittanceCreatorError]
        camps_remittance, error = CampsRemittanceCreator(CampsEdition.objects.all()).create()

        self.assertIsNotNone(camps_remittance)
        camps_receipt: CampsReceipt = CampsReceipt.objects.get(remittance=camps_remittance)
        self.assertAlmostEqual(camps_receipt.amount, camps_registration.calculate_price(), 2)
        self.assertIsNone(error)

    def test_create_camps_remittance_with_two_camps_registrations(self):
        baker.make(BankBicCode, bank_code='2095')
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        camps_edition: CampsEdition = baker.make(CampsEdition)
        holder: Holder = baker.make(Holder)
        baker.make(CampsRegistration, holder=holder, camps_edition=camps_edition, _quantity=2)

        camps_remittance: Optional[CampsRemittance]
        error: Optional[RemittanceCreatorError]
        camps_remittance, error = CampsRemittanceCreator(CampsEdition.objects.all()).create()

        self.assertIsNotNone(camps_remittance)
        self.assertEqual(CampsReceipt.objects.filter(remittance=camps_remittance).count(), 2)
        self.assertIsNone(error)
