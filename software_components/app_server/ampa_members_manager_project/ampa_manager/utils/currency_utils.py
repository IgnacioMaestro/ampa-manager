class CurrencyUtils:

    @classmethod
    def get_rounded_amount(cls, amount: float, decimals: int = 2):
        if amount:
            rounded_amount = round(amount, decimals)
            return f"{rounded_amount:.{decimals}f} €"
        return None
