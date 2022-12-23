from typing import List

from django.db.models import QuerySet

from ampa_members_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_members_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.charge.remittance import Remittance


class AfterSchoolRemittanceGenerator:
    def __init__(self, after_school_remittance: AfterSchoolRemittance):
        self.__after_school_remittance = after_school_remittance

    def generate(self) -> Remittance:
        receipts: List[Receipt] = []
        after_school_receipts: QuerySet[AfterSchoolReceipt] = AfterSchoolReceipt.objects.filter(
            remittance=self.__after_school_remittance)
        for after_school_receipt in after_school_receipts:
            receipts.append(after_school_receipt.generate_receipt())
        return Remittance(receipts, str(self.__after_school_remittance))
