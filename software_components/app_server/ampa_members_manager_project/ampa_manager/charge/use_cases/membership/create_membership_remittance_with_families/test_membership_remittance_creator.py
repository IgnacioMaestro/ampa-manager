from typing import Final, Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder


class TestRemittanceCreator(TestCase):
    course: AcademicCourse
    holder: Holder

    @classmethod
    def setUpTestData(cls):
        cls.course = baker.make(AcademicCourse)
        baker.make(BankBicCode, bank_code='2095')
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        cls.holder = baker.make(Holder, bank_account=bank_account)

    def test_create_with_no_family(self):
        # Act
        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreator(
            families=Family.objects.none(), course=self.course).create()

        # Assert
        self.assertIsNone(membership_remittance)
        self.assertEqual(0, MembershipRemittance.objects.count())
        self.assertEqual(0, MembershipReceipt.objects.count())
        self.assertEqual(error, RemittanceCreatorError.NO_FAMILIES)

    def test_create_with_family_with_bic_error(self):
        # Arrange
        baker.make(Family)

        # Act
        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        # Assert
        self.assertIsNone(membership_remittance)
        self.assertEqual(0, MembershipRemittance.objects.count())
        self.assertEqual(0, MembershipReceipt.objects.count())
        self.assertEqual(error, RemittanceCreatorError.BIC_ERROR)

    def test_create_with_family_with_no_fee_error(self):
        # Arrange
        baker.make(Family, membership_holder=self.holder)

        # Act
        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        # Assert
        self.assertIsNone(membership_remittance)
        self.assertEqual(0, MembershipRemittance.objects.count())
        self.assertEqual(0, MembershipReceipt.objects.count())
        self.assertEqual(error, RemittanceCreatorError.NO_FEE_FOR_COURSE)

    def test_create_with_a_family(self):
        # Arrange
        baker.make(Fee, academic_course=self.course)
        baker.make(Family, membership_holder=self.holder)

        # Act
        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        # Assert
        self.assertEqual(membership_remittance.course, self.course)
        self.assertEqual(membership_remittance.receipts.all().count(), 1)
        self.assertEqual(1, MembershipRemittance.objects.count())
        self.assertEqual(1, MembershipReceipt.objects.count())
        self.assertIsNone(error)

    def test_create_with_a_declined_family(self):
        # Arrange
        baker.make(Family, membership_holder=self.holder, decline_membership=True)

        # Act
        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        # Assert
        self.assertIsNone(membership_remittance)
        self.assertEqual(0, MembershipRemittance.objects.count())
        self.assertEqual(0, MembershipReceipt.objects.count())
        self.assertEqual(error, RemittanceCreatorError.NO_FAMILIES)

    def test_create_with_two_family(self):
        # Arrange
        baker.make(Fee, academic_course=self.course)
        quantity: Final[int] = 2
        baker.make(Family, membership_holder=self.holder, _quantity=quantity)

        # Act
        membership_remittance: Optional[MembershipRemittance]
        error: Optional[RemittanceCreatorError]
        membership_remittance, error = MembershipRemittanceCreator(
            families=Family.objects.all(), course=self.course).create()

        # Assert
        self.assertEqual(membership_remittance.course, self.course)
        self.assertEqual(membership_remittance.receipts.all().count(), quantity)
        self.assertEqual(1, MembershipRemittance.objects.count())
        self.assertEqual(2, MembershipReceipt.objects.count())
        self.assertIsNone(error)
