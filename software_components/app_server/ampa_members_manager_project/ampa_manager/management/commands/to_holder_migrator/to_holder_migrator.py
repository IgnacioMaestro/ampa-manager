from ampa_manager.family.models.authorization.authorization_old import AuthorizationOld
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder


class ToHolderMigrator:
    @classmethod
    def migrate(cls):
        for bank_account in BankAccount.objects.all().iterator():
            authorization_old: AuthorizationOld = AuthorizationOld.objects.of_bank_account(bank_account).get()
            holder: Holder = Holder.objects.create(
                parent=bank_account.owner, bank_account=bank_account, order=authorization_old.order,
                year=authorization_old.year, sign_date=authorization_old.sign_date, state=authorization_old.state)
            authorization_old.delete()
            try:
                family: Family = Family.objects.filter(default_bank_account=bank_account).get()
                family.default_holder = holder
                family.save()
            except Family.DoesNotExist:
                pass
