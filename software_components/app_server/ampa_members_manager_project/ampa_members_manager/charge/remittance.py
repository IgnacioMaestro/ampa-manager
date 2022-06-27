from typing import List

from ampa_members_manager.charge.receipt import Receipt


class Remittance:
    def __init__(self, receipts: List[Receipt], name: str):
        self.receipts: List[Receipt] = receipts
        self.name = name
