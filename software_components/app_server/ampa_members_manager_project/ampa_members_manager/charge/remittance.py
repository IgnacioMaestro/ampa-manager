from typing import List

from .receipt import Receipt


class Remittance:
    def __init__(self, receipts: List[Receipt], name: str):
        self.receipts: List[Receipt] = receipts
        self.name = name

    def obtain_rows(self) -> List[List[str]]:
        rows: List[List[str]] = []
        for receipt in self.receipts:
            rows.append(receipt.obtain_row())
        return rows
