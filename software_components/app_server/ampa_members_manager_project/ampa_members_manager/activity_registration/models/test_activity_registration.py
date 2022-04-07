from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family


class TestActivityRegistration(TestCase):
    def test_str_registered_family(self):
        family: Family = baker.make('Family')
        activity_registration: ActivityRegistration = baker.make(
            'ActivityRegistration', registered_child=None, registered_family=family)
        self.assertEqual(
            str(activity_registration),
            f'{str(activity_registration.single_activity)}-{str(activity_registration.registered_family)}')

    def test_str_registered_child(self):
        child: Child = baker.make('Child')
        activity_registration: ActivityRegistration = baker.make(
            'ActivityRegistration', registered_child=child, registered_family=None)
        self.assertEqual(
            str(activity_registration),
            f'{str(activity_registration.single_activity)}-{str(activity_registration.registered_child)}')
