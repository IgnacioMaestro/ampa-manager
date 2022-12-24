from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family
from ampa_manager.tests.generator_adder import bic_generator, phonenumbers_generator, iban_generator

baker.generators.add('localflavor.generic.models.BICField', bic_generator)
baker.generators.add('phonenumber_field.modelfields.PhoneNumberField', phonenumbers_generator)
baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


bank_account_local_recipe = Recipe(BankAccount)
family_bank_account_local_recipe = Recipe(Family, default_bank_account=foreign_key(bank_account_local_recipe))
