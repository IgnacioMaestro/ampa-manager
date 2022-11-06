from typing import Final

from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.charge.use_cases.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_members_manager.family.models.family import Family


class TestRemittanceCreator(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course: AcademicCourse = baker.make('AcademicCourse')

    def test_create_with_no_family(self):
        membership_remittance: MembershipRemittance = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        self.assertIsNone(membership_remittance)

    def test_create_with_a_family(self):
        baker.make('Family')

        membership_remittance: MembershipRemittance = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        self.assertEqual(membership_remittance.course, self.course)
        self.assertEqual(membership_remittance.membershipreceipt_set.all().count(), 1)

    def test_create_with_a_declined_family(self):
        baker.make('Family', decline_membership=True)

        membership_remittance: MembershipRemittance = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        self.assertIsNone(membership_remittance)

    def test_create_with_two_family(self):
        quantity: Final[int] = 2
        baker.make('Family', _quantity=quantity)

        membership_remittance: MembershipRemittance = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        self.assertEqual(membership_remittance.course, self.course)
        self.assertEqual(membership_remittance.membershipreceipt_set.all().count(), quantity)
