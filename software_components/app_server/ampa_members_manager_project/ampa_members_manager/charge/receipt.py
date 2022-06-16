from dataclasses import dataclass


@dataclass
class Receipt:
    amount: float
    bank_account_owner: str
    iban: str
    authorization: str

    def export_csv(self):
        return f'{self.amount},{self.bank_account_owner},{self.iban},{self.authorization}'
