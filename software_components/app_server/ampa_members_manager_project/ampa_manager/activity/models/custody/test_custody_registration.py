from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.membership import Membership
from ampa_manager.tests.generator_adder import iban_generator

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCustodyRegistration(TestCase):
    days_with_service = 10
    less_assisted_days = 2
    more_assisted_days = 9
    same_assisted_days = 8
    price_for_no_member = 5.5
    price_for_member = 3.5
    custody_registration_less_days: CustodyRegistration
    custody_registration_same_days: CustodyRegistration
    custody_registration_more_days: CustodyRegistration

    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        custody_edition: CustodyEdition = baker.make(
            CustodyEdition, days_with_service=cls.days_with_service, price_for_member=cls.price_for_member,
            price_for_no_member=cls.price_for_no_member)
        cls.custody_registration_less_days = baker.make(
            CustodyRegistration, custody_edition=custody_edition, assisted_days=cls.less_assisted_days)
        cls.custody_registration_same_days = baker.make(
            CustodyRegistration, custody_edition=custody_edition, assisted_days=cls.same_assisted_days)
        cls.custody_registration_more_days = baker.make(
            CustodyRegistration, custody_edition=custody_edition, assisted_days=cls.more_assisted_days)

    def test_meet_a_constraint(self):
        # Arrange
        baker.make(CustodyRegistration)

        # Act
        custody_registration: CustodyRegistration = baker.make(CustodyRegistration)

        # Assert
        self.assertIsNotNone(custody_registration)

    def test_no_meet_a_constraint(self):
        # Arrange
        custody_registration: CustodyRegistration = baker.make(CustodyRegistration)

        # Assert
        with self.assertRaises(IntegrityError):
            baker.make(
                CustodyRegistration, custody_edition=custody_registration.custody_edition,
                child=custody_registration.child)

    def test_calculate_price_for_no_member_assisted_days_less_than_max(self):
        # Act
        price: float = self.custody_registration_less_days.calculate_price()

        # Assert
        self.assertAlmostEqual(price, float(self.less_assisted_days * self.price_for_no_member), 2)

    def test_calculate_price_for_no_member_assisted_days_same_than_max(self):
        # Act
        price: float = self.custody_registration_same_days.calculate_price()

        # Assert
        expected_price = float(self.custody_registration_same_days.assisted_days * self.price_for_no_member)
        self.assertAlmostEqual(price, expected_price, 2)
        max_days_for_charge: int = self.custody_registration_more_days.custody_edition.max_days_for_charge
        self.assertAlmostEqual(price, float(max_days_for_charge * self.price_for_no_member), 2)

    def test_calculate_price_for_no_member_assisted_days_more_than_max(self):
        # Act
        price: float = self.custody_registration_more_days.calculate_price()

        # Assert
        max_days_for_charge: int = self.custody_registration_more_days.custody_edition.max_days_for_charge
        self.assertAlmostEqual(price, float(max_days_for_charge * self.price_for_no_member), 2)

    def test_calculate_price_for_member_assisted_days_less_than_max(self):
        # Arrange
        baker.make(
            Membership, family=self.custody_registration_less_days.child.family, academic_course=ActiveCourse.load())

        # Act
        price: float = self.custody_registration_less_days.calculate_price()

        # Assert
        self.assertAlmostEqual(price, float(self.less_assisted_days * self.price_for_member), 2)

    def test_calculate_price_for_member_assisted_days_same_than_max(self):
        # Arrange
        baker.make(
            Membership, family=self.custody_registration_same_days.child.family, academic_course=ActiveCourse.load())

        # Act
        price: float = self.custody_registration_same_days.calculate_price()

        # Assert
        expected_price: float = float(self.custody_registration_same_days.assisted_days * self.price_for_member)
        self.assertAlmostEqual(price, expected_price, 2)
        max_days_for_charge: int = self.custody_registration_more_days.custody_edition.max_days_for_charge
        self.assertAlmostEqual(price, float(max_days_for_charge * self.price_for_member), 2)

    def test_calculate_price_for_member_assisted_days_more_than_max(self):
        # Arrange
        baker.make(
            Membership, family=self.custody_registration_more_days.child.family, academic_course=ActiveCourse.load())

        # Act
        price: float = self.custody_registration_more_days.calculate_price()

        # Assert
        max_days_for_charge: int = self.custody_registration_more_days.custody_edition.max_days_for_charge
        self.assertAlmostEqual(price, float(max_days_for_charge * self.price_for_member), 2)
