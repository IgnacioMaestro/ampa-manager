from typing import Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.create_membership_remittance_for_unique_families.membership_remittance_creator_of_active_course import \
    MembershipRemittanceCreatorOfActiveCourse
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership


class TestMembershipRemittanceCreatorOfActiveCourse(TestCase):
    academic_course: AcademicCourse
    family: Family

    @classmethod
    def setUpTestData(cls):
        cls.academic_course = baker.make(AcademicCourse)
        ActiveCourse.objects.create(course=cls.academic_course)
        baker.make(BankBicCode, bank_code='2095')
        holder = baker.make(Holder)
        cls.family = baker.make(Family, membership_holder=holder)

    def test_create_no_membership(self):
        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)
        self.assertEqual(error, RemittanceCreatorError.NO_FAMILIES)

    def test_create_one_membership_for_other_year(self):
        baker.make(Membership)

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)
        self.assertEqual(error, RemittanceCreatorError.NO_FAMILIES)

    def test_create_one_membership_of_the_year_not_included(self):
        baker.make(Membership, family=self.family, academic_course=self.academic_course)

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.count(), 1)
        self.assertIsNone(error)

    def test_create_one_membership_of_the_year_not_included_but_family_declined(self):
        membership: Membership = baker.make(Membership, family=self.family, academic_course=self.academic_course)
        membership.family.decline_membership = True
        membership.family.save()

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)
        self.assertEqual(error, RemittanceCreatorError.NO_FAMILIES)

    def test_create_one_membership_of_the_year_not_included_because_receipt_other_year(self):
        membership: Membership = baker.make(Membership, family=self.family, academic_course=self.academic_course)
        baker.make(MembershipReceipt, family=membership.family)

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.filter(remittance=membership_remittance).count(), 1)
        self.assertEqual(MembershipReceipt.objects.count(), 2)
        self.assertIsNone(error)

    def test_create_one_membership_of_the_year_included(self):
        membership: Membership = baker.make(Membership, family=self.family, academic_course=self.academic_course)
        membership_remittance: MembershipRemittance = baker.make(MembershipRemittance, course=self.academic_course)
        baker.make(MembershipReceipt, family=membership.family, remittance=membership_remittance)

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)
        self.assertEqual(error, RemittanceCreatorError.NO_FAMILIES)

    def test_create_two_membership_of_the_year_not_included(self):
        baker.make(Membership, family=self.family, academic_course=self.academic_course)
        other_family = baker.make(Family, membership_holder=baker.make(Holder))
        baker.make(Membership, family=other_family, academic_course=self.academic_course)

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.count(), 2)
        self.assertIsNone(error)

    def test_create_two_membership_of_the_year_both_included(self):
        membership: Membership = baker.make(Membership, academic_course=self.academic_course)
        other_membership: Membership = baker.make(Membership, academic_course=self.academic_course)
        membership_remittance: MembershipRemittance = baker.make(MembershipRemittance, course=self.academic_course)
        baker.make(MembershipReceipt, family=membership.family, remittance=membership_remittance)
        baker.make(MembershipReceipt, family=other_membership.family, remittance=membership_remittance)

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNone(membership_remittance)
        self.assertEqual(error, RemittanceCreatorError.NO_FAMILIES)

    def test_create_two_membership_of_the_year_one_included_and_other_no(self):
        membership: Membership = baker.make(Membership, academic_course=self.academic_course)
        baker.make(Membership, family=self.family, academic_course=self.academic_course)
        membership_remittance: MembershipRemittance = baker.make(MembershipRemittance, course=self.academic_course)
        baker.make(MembershipReceipt, family=membership.family, remittance=membership_remittance)

        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreatorOfActiveCourse.create()

        self.assertIsNotNone(membership_remittance)
        self.assertEqual(MembershipReceipt.objects.filter(remittance=membership_remittance).count(), 1)
        self.assertEqual(MembershipReceipt.objects.count(), 2)
        self.assertIsNone(error)
