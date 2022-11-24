from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_members_manager.baker_recipes import bank_account_recipe


class TestAfterSchoolRegistration(TestCase):
    def test_meet_unique_constraint(self):
        baker.make('AfterSchoolRegistration', bank_account=baker.make_recipe(bank_account_recipe))

        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')

        self.assertIsNotNone(after_school_registration)

    def test_no_meet_unique_constraint(self):
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')

        with self.assertRaises(IntegrityError):
            baker.make(
                'AfterSchoolRegistration', after_school_edition=after_school_registration.after_school_edition,
                child=after_school_registration.child)

    def test_str(self):
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')
        self.assertEqual(
            str(after_school_registration),
            f'{after_school_registration.after_school_edition} {after_school_registration.child}')
