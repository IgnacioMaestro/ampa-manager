class BicCode:

    CODES = {
        "2100": "CAIXESBBXXX",
        "3035": "CLPEES2MXXX",
        "73": "OPENESMMXXX",
        "2095": "BASKES2BXXX",
        "3008": "BCOEESMM008",
        "81": "BSABESBBXXX",
        "239": "EVOBESMMXXX",
        "128": "BKBKESMMXXX",
        "2085": "CAZRES2ZXXX",
        "138": "BKOAES22XXX",
        "182": "BBVAESMMXXX",
        "216": "CMCIESMMXXX",
        "49": "BSCHESMMXXX",
        "1465": "INGDESMMXXX",
        "2080": "CAGLESMMXXX",
        "3076": "BCOEESMM076"
    }

    @staticmethod
    def get_bic_code(iban):
        bank_code = BicCode.extract_bank_code_from_iban(iban)
        return BicCode.CODES.get(str(bank_code), None)
    
    @staticmethod
    def extract_bank_code_from_iban(iban):
        if iban:
            temp = str(iban).replace(' ', '')
            if len(temp) == 24:
                return temp[4:8]
            elif len(temp) == 20:
                return temp[0:4]
        return None
