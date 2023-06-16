from typing import List

from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance


class MembershipRemittanceGenerator:
    __membership_remittance: MembershipRemittance

    def __init__(self, membership_remittance: MembershipRemittance):
        self.__membership_remittance = membership_remittance

    def generate(self) -> Remittance:
        receipts: List[Receipt] = []
        for membership_receipt in self.__membership_remittance.membershipreceipt_set.iterator():
            receipts.append(membership_receipt.generate_receipt())
        return Remittance(
            receipts=receipts, name=self.__membership_remittance.name, sepa_id=self.__membership_remittance.sepa_id,
            created_date=self.__membership_remittance.created_at,
            payment_date=self.__membership_remittance.payment_date, concept=self.__membership_remittance.concept)
