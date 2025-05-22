from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.half_amount_receipt_calculator import \
    HalfAmountReceiptCalculator


class TestHalfAmountReceiptCalculator(TestCase):
    def test_calculate(self):
        # Arrange
        ActiveCourse.objects.create(course=baker.make(AcademicCourse))
        after_school_registration: AfterSchoolRegistration = baker.make(AfterSchoolRegistration)

        # Act
        amount: float = HalfAmountReceiptCalculator().calculate(after_school_registration=after_school_registration)

        # Assert
        self.assertEqual(amount, after_school_registration.calculate_price() / 2)
