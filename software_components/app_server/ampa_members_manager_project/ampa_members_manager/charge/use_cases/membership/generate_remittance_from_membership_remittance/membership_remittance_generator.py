from typing import List

from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.charge.remittance import Remittance


class MembershipRemittanceGenerator:
    __membership_remittance: MembershipRemittance

    def __init__(self, membership_remittance: MembershipRemittance):
        self.__membership_remittance = membership_remittance

    def generate(self) -> Remittance:
        receipts: List[Receipt] = []
        for membership_receipt in self.__membership_remittance.membershipreceipt_set.all():
            receipts.append(membership_receipt.generate_receipt())
        return Remittance(receipts, str(self.__membership_remittance))
