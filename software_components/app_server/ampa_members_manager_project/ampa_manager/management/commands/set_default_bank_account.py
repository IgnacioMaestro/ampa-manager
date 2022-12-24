from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family


class Command(BaseCommand):
    help = 'Set default bank account for families with only 1 bank account'

    def handle(self, *args, **options):
        for family in Family.objects.without_default_bank_account():
            bank_accounts: QuerySet[BankAccount] = BankAccount.objects.of_family(family)
            if (bank_accounts.count()) == 1:
                family.default_bank_account = bank_accounts.first()
                family.save()
            else:
                print(f'Family {family}: not set. Accounts: {bank_accounts.count()}')
