from datetime import datetime
import re
import xlrd
import traceback

from django.core.management.base import BaseCommand
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
import ampa_members_manager.management.commands.members_excel_settings as xls_settings
from ampa_members_manager.family.models.family import Family

class Command(BaseCommand):
    help = 'Import families, parents, childs and bank accounts from an excel file'

    def handle(self, *args, **options):
        families_without_bank_account = Family.objects.filter(default_bank_account=None)
        for family in families_without_bank_account:
            if (BankAccount.objects.filter(owner__family=family).count()) == 1:
                family.default_bank_account = BankAccount.objects.filter(owner__family=family).first()
                family.save()
            else:
                print('Hay ' + str(BankAccount.objects.filter(owner__family=family).count()) + ' cuentas')
