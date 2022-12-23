from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AuthorizationReceipt:
    number: str
    date: Optional[str]


@dataclass
class Receipt:
    NO_AUTHORIZATION_MESSAGE = 'No authorization'
    amount: float
    bank_account_owner: str
    iban: str
    authorization: AuthorizationReceipt

    def obtain_row(self) -> List[str]:
        return ['"{}"'.format(str(self.amount)), str(self.bank_account_owner), str(self.iban),
                str(self.authorization.number), str(self.authorization.date)]
