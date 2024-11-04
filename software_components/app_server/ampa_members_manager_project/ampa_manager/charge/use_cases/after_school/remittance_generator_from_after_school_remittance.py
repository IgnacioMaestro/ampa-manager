from typing import Optional

from django.db.models import QuerySet

from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.models.receipt_exceptions import NoSwiftBicException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting
from ..remittance_creator_error import RemittanceCreatorError


class RemittanceGeneratorFromAfterSchoolRemittance:
    def __init__(self, after_school_remittance: AfterSchoolRemittance):
        self.__after_school_remittance = after_school_remittance

    def generate(self) -> tuple[Optional[Remittance], Optional[RemittanceCreatorError]]:
        receipts: list[Receipt] = []
        after_school_receipts: QuerySet[AfterSchoolReceipt] = AfterSchoolReceipt.objects.filter(
            remittance=self.__after_school_remittance)
        for after_school_receipt in after_school_receipts:
            try:
                receipt = after_school_receipt.generate_receipt()
                receipts.append(receipt)
            except NoSwiftBicException:
                return None, RemittanceCreatorError.BIC_ERROR
        bic: str = DynamicSetting.load().remittances_bic
        iban: str = DynamicSetting.load().remittances_iban
        return Remittance(
            receipts=receipts, name=self.__after_school_remittance.name, sepa_id=self.__after_school_remittance.sepa_id,
            created_date=self.__after_school_remittance.created_at,
            payment_date=self.__after_school_remittance.payment_date, concept=self.__after_school_remittance.concept,
            bic=bic, iban=iban), None
