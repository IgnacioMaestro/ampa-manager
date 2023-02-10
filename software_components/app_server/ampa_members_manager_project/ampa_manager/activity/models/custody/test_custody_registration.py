from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.tests.generator_adder import iban_generator

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestCustodyRegistration(TestCase):
    max_days_for_charge = 3
    less_assisted_days = 2
    more_assisted_days = 4
    price_for_no_member = 5.5
    price_for_member = 3.5
    custody_registration_less_days: CustodyRegistration
    custody_registration_same_days: CustodyRegistration
    custody_registration_more_days: CustodyRegistration

    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        custody_edition = baker.make(
            'CustodyEdition', max_days_for_charge=cls.max_days_for_charge, price_for_member=cls.price_for_member,
            price_for_no_member=cls.price_for_no_member)
        cls.custody_registration_less_days = baker.make(
            CustodyRegistration, custody_edition=custody_edition, assisted_days=cls.less_assisted_days)
        cls.custody_registration_same_days = baker.make(
            CustodyRegistration, custody_edition=custody_edition, assisted_days=cls.max_days_for_charge)
        cls.custody_registration_more_days = baker.make(
            CustodyRegistration, custody_edition=custody_edition, assisted_days=cls.more_assisted_days)

    def test_meet_a_constraint(self):
        baker.make('CustodyRegistration')

        custody_registration: CustodyRegistration = baker.make('CustodyRegistration')

        self.assertIsNotNone(custody_registration)

    def test_no_meet_a_constraint(self):
        custody_registration: CustodyRegistration = baker.make('CustodyRegistration')

        with self.assertRaises(IntegrityError):
            baker.make(
                'CustodyRegistration', custody_edition=custody_registration.custody_edition,
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
        self.assertAlmostEqual(
            price, float(self.custody_registration_same_days.assisted_days * self.price_for_no_member), 2)
        self.assertAlmostEqual(price, float(self.max_days_for_charge * self.price_for_no_member), 2)

    def test_calculate_price_for_no_member_assisted_days_more_than_max(self):
        # Act
        price: float = self.custody_registration_more_days.calculate_price()

        # Assert
        self.assertAlmostEqual(price, float(self.max_days_for_charge * self.price_for_no_member), 2)

    def test_calculate_price_for_member_assisted_days_less_than_max(self):
        # Arrange
        baker.make(
            'Membership', family=self.custody_registration_less_days.child.family, academic_course=ActiveCourse.load())

        # Act
        price: float = self.custody_registration_less_days.calculate_price()

        # Assert
        self.assertAlmostEqual(price, float(self.less_assisted_days * self.price_for_member), 2)

    def test_calculate_price_for_member_assisted_days_same_than_max(self):
        # Arrange
        baker.make(
            'Membership', family=self.custody_registration_same_days.child.family, academic_course=ActiveCourse.load())

        # Act
        price: float = self.custody_registration_same_days.calculate_price()

        # Assert
        self.assertAlmostEqual(
            price, float(self.custody_registration_same_days.assisted_days * self.price_for_member), 2)
        self.assertAlmostEqual(price, float(self.max_days_for_charge * self.price_for_member), 2)

    def test_calculate_price_for_member_assisted_days_more_than_max(self):
        # Arrange
        baker.make(
            'Membership', family=self.custody_registration_more_days.child.family, academic_course=ActiveCourse.load())

        # Act
        price: float = self.custody_registration_more_days.calculate_price()

        # Assert
        self.assertAlmostEqual(price, float(self.max_days_for_charge * self.price_for_member), 2)
