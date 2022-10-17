from django.core.management.base import BaseCommand
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.family import Family

class Command(BaseCommand):
    help = 'Set default bank acount for families without it and only 1 bank account'

    def handle(self, *args, **options):
        for family in Family.objects.without_default_account():
            if (BankAccount.objects.by_family(family).count()) == 1:
                family.default_bank_account = BankAccount.by_family(family).first()
                family.save()
            else:
                print(f'Family {family}: not set. Accounts: {BankAccount.objects.by_family(family).count()}')
