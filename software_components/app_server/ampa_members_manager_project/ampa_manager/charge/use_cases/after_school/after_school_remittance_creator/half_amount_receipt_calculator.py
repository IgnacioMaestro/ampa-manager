from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.amount_receipt_calculator import \
    AmountReceiptCalculator


class HalfAmountReceiptCalculator(AmountReceiptCalculator):

    def calculate(self, after_school_registration: AfterSchoolRegistration) -> float:
        return after_school_registration.calculate_price() / 2
