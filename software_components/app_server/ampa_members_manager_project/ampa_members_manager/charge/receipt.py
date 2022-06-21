from dataclasses import dataclass


@dataclass
class Receipt:
    amount: float
    bank_account_owner: str
    iban: str
    authorization: str

    def get_csv_properties(self):
        return [self.amount, self.bank_account_owner, self.iban, self.authorization]
