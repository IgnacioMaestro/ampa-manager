from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.tests.generator_adder import iban_generator
from .custody_remittance_creator import CustodyRemittanceCreator
from ....models.custody.custody_receipt import CustodyReceipt
from ....models.custody.custody_remittance import CustodyRemittance
from ....no_custody_edition_error import NoCustodyEditionError

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCustodyRemittanceCreator(TestCase):
    def test_create_no_after_school_edition(self):
        with self.assertRaises(NoCustodyEditionError):
            CustodyRemittanceCreator(CustodyEdition.objects.none()).create()

    def test_create_custody_edition_with_custody_registration(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        holder: Holder = baker.make('Holder')
        custody_registration: CustodyRegistration = baker.make('CustodyRegistration', holder=holder)

        custody_remittance: CustodyRemittance = CustodyRemittanceCreator(CustodyEdition.objects.all()).create()

        self.assertIsNotNone(custody_remittance)
        custody_receipt: CustodyReceipt = CustodyReceipt.objects.get(remittance=custody_remittance)
        self.assertAlmostEqual(custody_receipt.amount, custody_registration.calculate_price(), 2)

    def test_create_custody_edition_with_two_custody_registrations(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        custody_edition: CustodyEdition = baker.make('CustodyEdition')
        holder: Holder = baker.make('Holder')
        baker.make('CustodyRegistration', holder=holder, custody_edition=custody_edition, _quantity=2)

        custody_remittance: CustodyRemittance = CustodyRemittanceCreator(CustodyEdition.objects.all()).create()

        self.assertIsNotNone(custody_remittance)
        self.assertEqual(CustodyReceipt.objects.filter(remittance=custody_remittance).count(), 2)
