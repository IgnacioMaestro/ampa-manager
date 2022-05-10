from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.established_course import EstablishedCourse
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.activity_registration.models.familiar_activity_registration import \
    FamiliarActivityRegistration
from ampa_members_manager.activity_registration.models.individual_activity_registration import \
    IndividualActivityRegistration
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership


class TestActivityRegistration(TestCase):
    def setUp(self):
        self.academic_course: AcademicCourse = baker.make('AcademicCourse')
        EstablishedCourse.objects.create(course=self.academic_course)
        self.family: Family = baker.make('Family')
        self.familiar_activity_registration: FamiliarActivityRegistration = baker.make(
            'FamiliarActivityRegistration', registered_family=self.family)
        child: Child = baker.make('Child')
        self.individual_activity_registration: IndividualActivityRegistration = baker.make(
            'ActivityRegistration', registered_child=child)

    def test_str_registered_family(self):
        self.assertEqual(
            str(self.familiar_activity_registration),
            f'{str(self.familiar_activity_registration.single_activity)}-{str(self.familiar_activity_registration.registered_family)}')

    def test_str_registered_child(self):
        self.assertEqual(
            str(self.individual_activity_registration),
            f'{str(self.individual_activity_registration.single_activity)}-{str(self.individual_activity_registration.registered_child)}')

    def test_str_familiar_activity_registration(self):
        self.assertEqual(
            str(self.familiar_activity_registration),
            f'{str(self.familiar_activity_registration.single_activity)}-{str(self.familiar_activity_registration.registered_family)}')

    def test_str_individual_activity_registration(self):
        self.assertEqual(
            str(self.individual_activity_registration),
            f'{str(self.individual_activity_registration.single_activity)}-{str(self.individual_activity_registration.registered_child)}')

    def test_establish_amount(self):
        amount: float = 123.56
        child: Child = baker.make('Child')
        activity_registration: ActivityRegistration = baker.make(
            'ActivityRegistration', registered_child=child, registered_family=None)
        activity_registration.establish_amount(amount)
        activity_registration.refresh_from_db()
        self.assertEqual(activity_registration.amount, amount)

    def test_set_payment_order(self):
        payment_order_amount: float = 3.89
        self.assertIsNone(self.familiar_activity_registration.payment_order)
        self.familiar_activity_registration.set_payment_order(amount=payment_order_amount)
        self.familiar_activity_registration.refresh_from_db()
        self.assertIsNotNone(self.familiar_activity_registration.payment_order)
        self.assertEqual(self.familiar_activity_registration.payment_order.amount, payment_order_amount)

    def test_with_single_activity_no_activity_registration(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_single_activity(
            single_activity=single_activity)
        self.assertEqual(activity_registrations.count(), 0)

    def test_with_single_activity_one_activity_registration(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        child: Child = baker.make('Child')
        baker.make(
            'ActivityRegistration', registered_child=child, registered_family=None, single_activity=single_activity)
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_single_activity(
            single_activity=single_activity)
        self.assertEqual(activity_registrations.count(), 1)

    def test_with_single_activity_more_than_one_activity_registration(self):
        quantity: int = 3
        single_activity: SingleActivity = baker.make('SingleActivity')
        child: Child = baker.make('Child')
        baker.make(
            'ActivityRegistration',
            registered_child=child, registered_family=None, single_activity=single_activity,
            _quantity=quantity)
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_single_activity(
            single_activity=single_activity)
        self.assertEqual(activity_registrations.count(), quantity)

    def test_is_membership_no_membership(self):
        self.assertFalse(self.familiar_activity_registration.is_membership())
        self.assertFalse(self.individual_activity_registration.is_membership())

    def test_is_membership_membership(self):
        Membership.objects.create(
            family=self.familiar_activity_registration.registered_family, academic_course=self.academic_course)
        self.assertTrue(self.familiar_activity_registration.is_membership())
        Membership.objects.create(
            family=self.individual_activity_registration.registered_child.family, academic_course=self.academic_course)
        self.assertTrue(self.individual_activity_registration.is_membership())
