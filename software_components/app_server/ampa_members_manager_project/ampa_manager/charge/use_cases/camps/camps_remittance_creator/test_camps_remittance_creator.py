from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.tests.generator_adder import iban_generator
from .camps_remittance_creator import CampsRemittanceCreator
from ....models.camps.camps_receipt import CampsReceipt
from ....models.camps.camps_remittance import CampsRemittance
from ....no_camps_edition_error import NoCampsEditionError

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCampsRemittanceCreator(TestCase):
    def test_create_no_after_school_edition(self):
        with self.assertRaises(NoCampsEditionError):
            CampsRemittanceCreator(CampsEdition.objects.none()).create()

    def test_create_camps_edition_with_camps_registration(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        holder: Holder = baker.make('Holder')
        camps_registration: CampsRegistration = baker.make('CampsRegistration', holder=holder)

        camps_remittance: CampsRemittance = CampsRemittanceCreator(CampsEdition.objects.all()).create()

        self.assertIsNotNone(camps_remittance)
        camps_receipt: CampsReceipt = CampsReceipt.objects.get(remittance=camps_remittance)
        self.assertAlmostEqual(camps_receipt.amount, camps_registration.calculate_price(), 2)

    def test_create_camps_edition_with_two_camps_registrations(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        camps_edition: CampsEdition = baker.make('CampsEdition')
        holder: Holder = baker.make('Holder')
        baker.make('CampsRegistration', holder=holder, camps_edition=camps_edition, _quantity=2)

        camps_remittance: CampsRemittance = CampsRemittanceCreator(CampsEdition.objects.all()).create()

        self.assertIsNotNone(camps_remittance)
        self.assertEqual(CampsReceipt.objects.filter(remittance=camps_remittance).count(), 2)
