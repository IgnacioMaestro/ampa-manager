from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_members_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_members_manager.baker_recipes import bank_account_recipe
from ampa_members_manager.family.models.child import Child


class TestAfterSchoolRegistration(TestCase):
    def test_meet_unique_constraint(self):
        baker.make('AfterSchoolRegistration', bank_account=baker.make_recipe(bank_account_recipe))

        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')

        self.assertIsNotNone(after_school_registration)

    def test_no_meet_unique_constraint(self):
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')

        with self.assertRaises(IntegrityError):
            child: Child = after_school_registration.child
            after_school_edition: AfterSchoolEdition = after_school_registration.after_school_edition
            baker.make('AfterSchoolRegistration', after_school_edition=after_school_edition, child=child)

    def test_str(self):
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')
        self.assertEqual(
            str(after_school_registration),
            f'{after_school_registration.after_school_edition} {after_school_registration.child}')

    def test_calculate_price_for_no_member(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')

        # Act
        price: float = after_school_registration.calculate_price()

        # Assert
        self.assertEqual(price, float(after_school_registration.after_school_edition.price_for_no_member))

    def test_calculate_price_for_member(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')
        family = after_school_registration.child.family
        baker.make('Membership', family=family, academic_course=ActiveCourse.load())

        # Act
        price: float = after_school_registration.calculate_price()

        # Assert
        self.assertEqual(price, float(after_school_registration.after_school_edition.price_for_member))
