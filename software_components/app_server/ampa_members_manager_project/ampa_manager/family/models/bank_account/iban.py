import string


class IBAN:
    LETTERS = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}

    @staticmethod
    def convert_iban_into_number(iban):
        return (iban[4:] + iban[:4]).translate(IBAN.LETTERS)

    @staticmethod
    def generate_iban_check_digits(iban):
        number_iban = IBAN.convert_iban_into_number(iban[:2] + '00' + iban[4:])
        return '{:0>2}'.format(98 - (int(number_iban) % 97))

    @staticmethod
    def is_valid(iban: str):
        if len(str(iban)) >= 22:
            return IBAN.generate_iban_check_digits(str(iban)) == str(iban)[2:4] and \
                int(IBAN.convert_iban_into_number(str(iban))) % 97 == 1
        return

    @staticmethod
    def get_bank_code(iban: str):
        if iban:
            if len(iban) == 24:
                return iban[4:8]
            elif len(iban) == 20:
                return iban[0:4]
        return None
