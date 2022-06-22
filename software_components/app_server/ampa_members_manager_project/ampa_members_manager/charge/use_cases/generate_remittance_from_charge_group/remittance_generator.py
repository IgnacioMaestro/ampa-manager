from typing import List

from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.charge.remittance import Remittance


class RemittanceGenerator:
    @classmethod
    def generate(cls, charge_group: ChargeGroup, remittance_name: str) -> Remittance:
        receipts: List[Receipt] = []
        for charge in charge_group.charge_set.all():
            receipts.append(charge.generate_receipt())
        return Remittance(receipts, remittance_name)
