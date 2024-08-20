from typing import Optional

from django.db.models import QuerySet

from ampa_manager.charge.models.custody.custody_receipt import CustodyReceipt
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.models.receipt_exceptions import NoSwiftBicException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError


class RemittanceGeneratorFromCustodyRemittance:
    def __init__(self, custody_remittance: CustodyRemittance):
        self.__custody_remittance = custody_remittance

    def generate(self) -> tuple[Optional[Remittance], Optional[RemittanceCreatorError]]:
        receipts: list[Receipt] = []
        custody_receipts: QuerySet[CustodyReceipt] = CustodyReceipt.objects.filter(
            remittance=self.__custody_remittance)
        for custody_receipt in custody_receipts:
            try:
                receipt = custody_receipt.generate_receipt()
                receipts.append(receipt)
            except NoSwiftBicException:
                return None, RemittanceCreatorError.BIC_ERROR
        remittance = Remittance(
            receipts=receipts, name=self.__custody_remittance.name, sepa_id=self.__custody_remittance.sepa_id,
            created_date=self.__custody_remittance.created_at, payment_date=self.__custody_remittance.payment_date,
            concept=self.__custody_remittance.concept)
        return remittance, None
