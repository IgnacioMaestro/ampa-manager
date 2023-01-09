from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from .amount_receipt_calculator import AmountReceiptCalculator


class FullAmountReceiptCalculator(AmountReceiptCalculator):
    def calculate(self, after_school_registration: AfterSchoolRegistration) -> float:
        return after_school_registration.calculate_price()
