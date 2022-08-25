from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestActivityRegistration(TestCase):
    def setUp(self):
        self.academic_course: AcademicCourse = baker.make('AcademicCourse')
        ActiveCourse.objects.create(course=self.academic_course)
        self.family: Family = baker.make('Family')
        self.activity_registration: ActivityRegistration = baker.make('ActivityRegistration')

    def test_str(self):
        self.assertEqual(
            str(self.activity_registration),
            f'{str(self.activity_registration.payable_part)}-{str(self.activity_registration.child)}')

    def test_establish_amount(self):
        amount: float = 123.56
        self.activity_registration.establish_amount(amount)
        self.activity_registration.refresh_from_db()
        self.assertEqual(self.activity_registration.amount, amount)

    def test_with_payable_part_no_activity_registration(self):
        payable_part: ActivityPeriod = baker.make('ActivityPeriod')
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_payable_part(
            payable_part=payable_part)
        self.assertEqual(activity_registrations.count(), 0)

    def test_with_payable_part_one_activity_registration(self):
        activity_period: ActivityPeriod = baker.make('ActivityPeriod')
        baker.make('ActivityRegistration', payable_part=activity_period)
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_payable_part(
            payable_part=activity_period)
        self.assertEqual(activity_registrations.count(), 1)

    def test_with_payable_part_more_than_one_activity_registration(self):
        quantity: int = 3
        activity_period: ActivityPeriod = baker.make('ActivityPeriod')
        baker.make('ActivityRegistration', payable_part=activity_period, _quantity=quantity)
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_payable_part(
            payable_part=activity_period)
        self.assertEqual(activity_registrations.count(), quantity)

    def test_is_membership_no_membership(self):
        self.assertFalse(self.activity_registration.is_membership())

    def test_is_membership_membership(self):
        Membership.objects.create(
            family=self.activity_registration.child.family, academic_course=self.academic_course)
        self.assertTrue(self.activity_registration.is_membership())
