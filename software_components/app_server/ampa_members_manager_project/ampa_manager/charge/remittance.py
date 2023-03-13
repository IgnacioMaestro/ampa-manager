from datetime import datetime, date
from typing import List

from .receipt import Receipt


class Remittance:
    def __init__(self, receipts: List[Receipt], name: str, created_date: datetime, payment_date: date, concept: str):
        self.receipts: List[Receipt] = receipts
        self.name: str = name
        self.created_date: datetime = created_date
        self.payment_date: date = payment_date
        self.concept: str = concept

    def obtain_rows(self) -> List[List[str]]:
        rows: List[List[str]] = []
        for receipt in self.receipts:
            rows.append(receipt.obtain_row())
        return rows
