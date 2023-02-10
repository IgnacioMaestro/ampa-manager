from django.db.models import QuerySet

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.after_school.after_school_registration_queryset import \
    AfterSchoolRegistrationQuerySet
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.amount_receipt_calculator import \
    AmountReceiptCalculator
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.full_amount_receipt_calculator import \
    FullAmountReceiptCalculator
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.half_amount_receipt_calculator import \
    HalfAmountReceiptCalculator
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.left_amount_receipt_calculator import \
    LeftAmountReceiptCalculator


class AfterSchoolRemittanceCreator:
    def __init__(self, editions: QuerySet[AfterSchoolEdition]):
        self.__editions: QuerySet[AfterSchoolEdition] = editions

    def create_full(self) -> AfterSchoolRemittance:
        return self.create_with_calculator(calculator=FullAmountReceiptCalculator())

    def create_half(self) -> AfterSchoolRemittance:
        return self.create_with_calculator(calculator=HalfAmountReceiptCalculator())

    def create_left(self) -> AfterSchoolRemittance:
        return self.create_with_calculator(calculator=LeftAmountReceiptCalculator())

    def create_with_calculator(self, calculator: AmountReceiptCalculator):
        after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittance.objects.create_filled(self.__editions)
        after_school_registrations: AfterSchoolRegistrationQuerySet = AfterSchoolRegistration.objects.of_after_school_remittance(
            after_school_remittance)
        for after_school_registration in after_school_registrations.iterator():
            AfterSchoolReceipt.objects.create(
                amount=calculator.calculate(after_school_registration), remittance=after_school_remittance,
                after_school_registration=after_school_registration)
        return after_school_remittance
