import random

import phonenumbers
from model_bakery import baker
from schwifty import IBAN, BIC


def phonenumbers_generator():
    return phonenumbers.parse('695715902', 'ES')


def iban_generator():
    return IBAN.generate('ES', bank_code='2095', account_code=str(random.randint(0, 99999)))


def bic_generator():
    return BIC.from_bank_code('ES', bank_code='2095')


class GeneratorAdder:
    @classmethod
    def add_all(cls):
        baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', phonenumbers_generator)
        baker.generators.add('localflavor.generic.models.IBANField', iban_generator)
        baker.generators.add('localflavor.generic.models.BICField', bic_generator)
