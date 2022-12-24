from typing import Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.create_membership_remittance_for_unique_families.membership_remittance_creator_of_active_course import \
    MembershipRemittanceCreatorOfActiveCourse
from ampa_manager.family.models.membership import Membership


class TestMembershipRemittanceCreatorOfActiveCourse(TestCase):

    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))

    def test_create_no_membership(self):
        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)

    def test_create_one_membership_for_other_year(self):
        baker.make('Membership')

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)

    def test_create_one_membership_of_the_year_not_included(self):
        baker.make('Membership', academic_course=ActiveCourse.load())

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.count(), 1)

    def test_create_one_membership_of_the_year_not_included_but_family_declined(self):
        membership: Membership = baker.make('Membership', academic_course=ActiveCourse.load())
        membership.family.decline_membership = True
        membership.family.save()

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)

    def test_create_one_membership_of_the_year_not_included_because_receipt_other_year(self):
        membership: Membership = baker.make('Membership', academic_course=ActiveCourse.load())
        baker.make('MembershipReceipt', family=membership.family)

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.filter(remittance=membership_remittance).count(), 1)
        self.assertEqual(MembershipReceipt.objects.count(), 2)

    def test_create_one_membership_of_the_year_included(self):
        membership: Membership = baker.make('Membership', academic_course=ActiveCourse.load())
        membership_remittance: MembershipRemittance = baker.make('MembershipRemittance', course=ActiveCourse.load())
        baker.make('MembershipReceipt', family=membership.family, remittance=membership_remittance)

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)

    def test_create_two_membership_of_the_year_not_included(self):
        baker.make('Membership', academic_course=ActiveCourse.load())
        baker.make('Membership', academic_course=ActiveCourse.load())

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.count(), 2)

    def test_create_two_membership_of_the_year_both_included(self):
        membership: Membership = baker.make('Membership', academic_course=ActiveCourse.load())
        other_membership: Membership = baker.make('Membership', academic_course=ActiveCourse.load())
        membership_remittance: MembershipRemittance = baker.make('MembershipRemittance', course=ActiveCourse.load())
        baker.make('MembershipReceipt', family=membership.family, remittance=membership_remittance)
        baker.make('MembershipReceipt', family=other_membership.family, remittance=membership_remittance)

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)

    def test_create_two_membership_of_the_year_one_included_and_other_no(self):
        membership: Membership = baker.make('Membership', academic_course=ActiveCourse.load())
        baker.make('Membership', academic_course=ActiveCourse.load())
        membership_remittance: MembershipRemittance = baker.make('MembershipRemittance', course=ActiveCourse.load())
        baker.make('MembershipReceipt', family=membership.family, remittance=membership_remittance)

        membership_remittance: Optional[MembershipRemittance] = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.filter(remittance=membership_remittance).count(), 1)
        self.assertEqual(MembershipReceipt.objects.count(), 2)
