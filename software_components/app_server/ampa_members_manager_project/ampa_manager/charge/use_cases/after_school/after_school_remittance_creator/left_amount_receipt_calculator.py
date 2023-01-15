from django.db.models import QuerySet

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.amount_receipt_calculator import \
    AmountReceiptCalculator


class LeftAmountReceiptCalculator(AmountReceiptCalculator):
    def calculate(self, after_school_registration: AfterSchoolRegistration) -> float:
        amount_in_receipts: float = self.calculate_amount_in_receipts(after_school_registration)
        if amount_in_receipts > after_school_registration.calculate_price():
            return 0.0
        else:
            return after_school_registration.calculate_price() - amount_in_receipts

    @classmethod
    def calculate_amount_in_receipts(cls, after_school_registration) -> float:
        after_school_receipts: QuerySet[AfterSchoolReceipt] = AfterSchoolReceipt.objects.filter(
            after_school_registration=after_school_registration)
        amount_in_receipts = 0.0
        for after_school_receipt in after_school_receipts.iterator():
            amount_in_receipts += after_school_receipt.amount

        return amount_in_receipts
