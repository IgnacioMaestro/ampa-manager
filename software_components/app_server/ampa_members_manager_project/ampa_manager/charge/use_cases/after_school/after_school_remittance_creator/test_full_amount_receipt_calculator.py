from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from .full_amount_receipt_calculator import FullAmountReceiptCalculator


class TestFullAmountReceiptCalculator(TestCase):
    def test_calculate(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')
        amount: float = FullAmountReceiptCalculator().calculate(after_school_registration=after_school_registration)
        self.assertEqual(amount, after_school_registration.calculate_price())
