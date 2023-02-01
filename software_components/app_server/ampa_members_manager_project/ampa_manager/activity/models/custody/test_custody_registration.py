from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.tests.generator_adder import iban_generator

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCustodyRegistration(TestCase):
    def test_meet_a_constraint(self):
        baker.make('CustodyRegistration')

        custody_registration: CustodyRegistration = baker.make('CustodyRegistration')

        self.assertIsNotNone(custody_registration)

    def test_no_meet_a_constraint(self):
        custody_registration: CustodyRegistration = baker.make('CustodyRegistration')

        with self.assertRaises(IntegrityError):
            baker.make(
                'CustodyRegistration', custody_edition=custody_registration.custody_edition,
                child=custody_registration.child)
