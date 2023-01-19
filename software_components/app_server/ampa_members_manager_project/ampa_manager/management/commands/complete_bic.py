from django.core.management.base import BaseCommand

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.bank_account.bic_code import BicCode


class Command(BaseCommand):
    help = 'Calculate and complete BIC code from IBAN'

    def handle(self, *args, **options):
        for bank_account in BankAccount.objects.without_swift_bic():
            swift_bic = BicCode.get_bic_code(bank_account.iban)

            if swift_bic:
                bank_account.swift_bic = swift_bic
                bank_account.save()
                print(f'Bank account {bank_account}. BIC completed: {bank_account.swift_bic}')
            else:
                print(f'Bank account {bank_account}. BIC: not found')
