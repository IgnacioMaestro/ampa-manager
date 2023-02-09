from django.db.models import QuerySet

from ampa_manager.charge.models.custody.custody_receipt import CustodyReceipt
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance


class RemittanceGeneratorFromCustodyRemittance:
    def __init__(self, custody_remittance: CustodyRemittance):
        self.__custody_remittance = custody_remittance

    def generate(self) -> Remittance:
        receipts: list[Receipt] = []
        custody_receipts: QuerySet[CustodyReceipt] = CustodyReceipt.objects.filter(
            remittance=self.__custody_remittance)
        for custody_receipt in custody_receipts:
            receipts.append(custody_receipt.generate_receipt())
        return Remittance(receipts, self.__custody_remittance.name)
