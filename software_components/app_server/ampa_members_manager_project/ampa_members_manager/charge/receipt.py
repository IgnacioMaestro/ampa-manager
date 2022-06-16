from dataclasses import dataclass


@dataclass
class Receipt:
    amount: float
    bank_account_owner: str
    iban: str
    authorization: str
