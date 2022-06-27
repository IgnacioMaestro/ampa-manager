from typing import List

from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.charge.remittance import Remittance


class RemittanceGenerator:
    def __init__(self, charge_group: ChargeGroup, name: str):
        self.__charge_group: ChargeGroup = charge_group
        self.__name: str = name

    def generate(self) -> Remittance:
        receipts: List[Receipt] = []
        for charge in self.__charge_group.charge_set.all():
            receipts.append(charge.generate_receipt())
        return Remittance(receipts, self.__name)
