from typing import List, Optional, Final

from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.models.receipt_exceptions import NoFeeForCourseException, \
    NoSwiftBicException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance


class MembershipRemittanceGenerator:
    ERROR_SWIFT_BIC_REQUIRED: Final[str] = 'Swift BIC is required for bank accounts'
    __membership_remittance: MembershipRemittance

    def __init__(self, membership_remittance: MembershipRemittance):
        self.__membership_remittance = membership_remittance

    def generate(self) -> tuple[Optional[Remittance], Optional[str]]:
        is_error, receipts = self.generate_receipts()
        if is_error:
            return None, self.ERROR_SWIFT_BIC_REQUIRED
        remittance = Remittance(
            receipts=receipts, name=self.__membership_remittance.name, sepa_id=self.__membership_remittance.sepa_id,
            created_date=self.__membership_remittance.created_at,
            payment_date=self.__membership_remittance.payment_date, concept=self.__membership_remittance.concept)
        return remittance, None

    def generate_receipts(self) -> tuple[bool, List[Receipt]]:
        receipts: List[Receipt] = []
        is_error: bool = False
        for membership_receipt in self.__membership_remittance.membershipreceipt_set.iterator():
            try:
                receipt: Receipt = membership_receipt.generate_receipt()
                receipts.append(receipt)
            except NoFeeForCourseException:
                is_error = True
                break
            except NoSwiftBicException:
                is_error = True
                break
        return is_error, receipts
