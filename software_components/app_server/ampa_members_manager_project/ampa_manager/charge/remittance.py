from datetime import datetime, date
from typing import List
import copy
from datetime import date, datetime
from typing import List, Optional

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

    def calculate_total_amount(self) -> float:
        total_amount = 0.0
        for receipt in self.receipts:
            total_amount += receipt.amount
        return total_amount

    def obtain_receipts_grouped_by_iban(self) -> list[Receipt]:
        grouped_receipts: list[Receipt] = []
        for receipt in self.receipts:
            previous_receipt_with_iban = self.__search_in_receipts_by_iban(grouped_receipts, receipt.iban)
            if previous_receipt_with_iban is not None:
                previous_receipt_with_iban.amount += receipt.amount
            else:
                grouped_receipts.append(copy.deepcopy(receipt))
        return grouped_receipts

    @classmethod
    def __search_in_receipts_by_iban(cls, receipts: list[Receipt], iban: str) -> Optional[Receipt]:
        for receipt in receipts:
            if receipt.iban == iban:
                return receipt
        return None
