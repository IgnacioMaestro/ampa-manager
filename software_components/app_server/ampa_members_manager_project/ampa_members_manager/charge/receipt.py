from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Receipt:
    NO_AUTHORIZATION_MESSAGE = 'No authorization'
    amount: str
    bank_account_owner: str
    iban: str
    authorization_number: str
    authorization_date: Optional[str]

    def obtain_row(self) -> List[str]:
        return ['"{}"'.format(self.amount), str(self.bank_account_owner), str(self.iban), str(self.authorization_number), str(self.authorization_date)]
