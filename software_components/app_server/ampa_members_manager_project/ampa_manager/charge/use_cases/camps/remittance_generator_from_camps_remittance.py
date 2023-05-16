from django.db.models import QuerySet

from ampa_manager.charge.models.camps.camps_receipt import CampsReceipt
from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance


class RemittanceGeneratorFromCampsRemittance:
    def __init__(self, camps_remittance: CampsRemittance):
        self.__camps_remittance = camps_remittance

    def generate(self) -> Remittance:
        receipts: list[Receipt] = []
        camps_receipts: QuerySet[CampsReceipt] = CampsReceipt.objects.filter(
            remittance=self.__camps_remittance)
        for camps_receipt in camps_receipts:
            receipts.append(camps_receipt.generate_receipt())
        return Remittance(
            receipts=receipts, name=self.__camps_remittance.name, created_date=self.__camps_remittance.created_at,
            payment_date=self.__camps_remittance.payment_date, concept=self.__camps_remittance.concept)
