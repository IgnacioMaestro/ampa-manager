from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.established_course import EstablishedCourse
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership


class TestActivityRegistration(TestCase):
    def setUp(self):
        self.academic_course: AcademicCourse = baker.make('AcademicCourse')
        EstablishedCourse.objects.create(course=self.academic_course)
        self.family: Family = baker.make('Family')
        self.activity_registration: ActivityRegistration = baker.make('ActivityRegistration')

    def test_str(self):
        self.assertEqual(
            str(self.activity_registration),
            f'{str(self.activity_registration.single_activity)}-{str(self.activity_registration.child)}')

    def test_establish_amount(self):
        amount: float = 123.56
        self.activity_registration.establish_amount(amount)
        self.activity_registration.refresh_from_db()
        self.assertEqual(self.activity_registration.amount, amount)

    def test_set_payment_order(self):
        payment_order_amount: float = 3.89
        self.assertIsNone(self.activity_registration.payment_order)
        self.activity_registration.set_payment_order(amount=payment_order_amount)
        self.activity_registration.refresh_from_db()
        self.assertIsNotNone(self.activity_registration.payment_order)
        self.assertEqual(self.activity_registration.payment_order, payment_order_amount)

    def test_with_single_activity_no_activity_registration(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_single_activity(
            single_activity=single_activity)
        self.assertEqual(activity_registrations.count(), 0)

    def test_with_single_activity_one_activity_registration(self):
        single_activity: SingleActivity = baker.make('SingleActivity')
        baker.make('ActivityRegistration', single_activity=single_activity)
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_single_activity(
            single_activity=single_activity)
        self.assertEqual(activity_registrations.count(), 1)

    def test_with_single_activity_more_than_one_activity_registration(self):
        quantity: int = 3
        single_activity: SingleActivity = baker.make('SingleActivity')
        baker.make('ActivityRegistration', single_activity=single_activity, _quantity=quantity)
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_single_activity(
            single_activity=single_activity)
        self.assertEqual(activity_registrations.count(), quantity)

    def test_is_membership_no_membership(self):
        self.assertFalse(self.activity_registration.is_membership())

    def test_is_membership_membership(self):
        Membership.objects.create(
            family=self.activity_registration.child.family, academic_course=self.academic_course)
        self.assertTrue(self.activity_registration.is_membership())
