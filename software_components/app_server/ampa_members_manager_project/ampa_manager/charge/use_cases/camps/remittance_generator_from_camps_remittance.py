from typing import Optional

from django.db.models import QuerySet

from ampa_manager.charge.models.camps.camps_receipt import CampsReceipt
from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance
from ampa_manager.charge.models.receipt_exceptions import NoSwiftBicException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting


class RemittanceGeneratorFromCampsRemittance:
    def __init__(self, camps_remittance: CampsRemittance):
        self.__camps_remittance = camps_remittance

    def generate(self) -> tuple[Optional[Remittance], Optional[RemittanceCreatorError]]:
        receipts: list[Receipt] = []
        camps_receipts: QuerySet[CampsReceipt] = CampsReceipt.objects.filter(
            remittance=self.__camps_remittance)
        for camps_receipt in camps_receipts:
            try:
                receipt = camps_receipt.generate_receipt()
                receipts.append(receipt)
            except NoSwiftBicException:
                return None, RemittanceCreatorError.BIC_ERROR
        bic: str = DynamicSetting.load().remittances_bic
        iban: str = DynamicSetting.load().remittances_iban
        remittance = Remittance(
            receipts=receipts, name=self.__camps_remittance.name, sepa_id=self.__camps_remittance.sepa_id,
            created_date=self.__camps_remittance.created_at, payment_date=self.__camps_remittance.payment_date,
            concept=self.__camps_remittance.concept, bic=bic, iban=iban)
        return remittance, None
