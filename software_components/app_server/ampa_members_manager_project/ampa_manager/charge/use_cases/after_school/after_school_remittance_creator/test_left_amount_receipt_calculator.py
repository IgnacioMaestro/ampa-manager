from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.left_amount_receipt_calculator import \
    LeftAmountReceiptCalculator


class TestLeftAmountReceiptCalculator(TestCase):
    def test_calculate_no_previous_after_school_receipt(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')
        amount: float = LeftAmountReceiptCalculator().calculate(after_school_registration=after_school_registration)
        self.assertAlmostEqual(amount, after_school_registration.calculate_price(), 3)

    def test_calculate_previous_after_school_receipt_with_a_third(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_registration: AfterSchoolRegistration = baker.make('AfterSchoolRegistration')
        total_amount = after_school_registration.calculate_price()
        third_of_amount = total_amount / 3
        baker.make('AfterSchoolReceipt', after_school_registration=after_school_registration, amount=third_of_amount)
        amount: float = LeftAmountReceiptCalculator().calculate(after_school_registration=after_school_registration)
        self.assertAlmostEqual(amount, third_of_amount * 2, 3)
