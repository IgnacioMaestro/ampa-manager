class BankAccountImportedFields:

    def __init__(self, swift_bic, iban, is_default_account):
        self.swift_bic = swift_bic
        self.iban = iban
        self.is_default_account = is_default_account

    def get_list(self):
        return [self.swift_bic, self.iban, self.is_default_account]
