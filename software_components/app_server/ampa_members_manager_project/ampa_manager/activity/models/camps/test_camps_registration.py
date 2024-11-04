from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.tests.generator_adder import iban_generator

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCampsRegistration(TestCase):
    def test_meet_unique_academic_course_with_levels_constraint(self):
        baker.make(CampsRegistration)

        camps_registration: CampsRegistration = baker.make(CampsRegistration)

        self.assertIsNotNone(camps_registration)

    def test_no_meet_unique_academic_course_with_levels_constraint(self):
        camps_registration: CampsRegistration = baker.make(CampsRegistration)

        with self.assertRaises(IntegrityError):
            baker.make(
                CampsRegistration, camps_edition=camps_registration.camps_edition, child=camps_registration.child)
