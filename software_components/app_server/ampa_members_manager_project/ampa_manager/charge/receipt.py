import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AuthorizationReceipt:
    number: str
    date: datetime.date

    def obtain_date(self) -> str:
        return self.date.strftime("%m/%d/%Y")


@dataclass
class Receipt:
    NO_AUTHORIZATION_MESSAGE = 'No authorization'
    amount: float
    bank_account_owner: str
    iban: str
    bic: str
    authorization: Optional[AuthorizationReceipt]

    def obtain_row(self) -> List[str]:

        return [self.bank_account_owner, self.bic, self.iban, self.obtain_authorization_number(),
                self.obtain_date(), self.obtain_formatted_amount()]

    def obtain_formatted_amount(self) -> str:
        amount_2_decimals = f'{self.amount:.2f}'
        return amount_2_decimals.replace('.', ',')

    def obtain_authorization_number(self) -> str:
        number = Receipt.NO_AUTHORIZATION_MESSAGE
        if self.authorization is not None:
            number = self.authorization.number
        return number

    def obtain_date(self) -> str:
        str_date = ''
        if self.authorization is not None:
            str_date = self.authorization.obtain_date()
        return str_date
