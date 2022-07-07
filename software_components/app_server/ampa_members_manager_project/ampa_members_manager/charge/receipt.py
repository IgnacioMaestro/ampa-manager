from dataclasses import dataclass
from typing import List


@dataclass
class Receipt:
    amount: float
    bank_account_owner: str
    iban: str
    authorization: str

    def obtain_row(self) -> List[str]:
        return [self.amount, self.bank_account_owner, self.iban, self.authorization]
