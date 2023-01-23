from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
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

    @classmethod
    def migrate_after_school_registrations(cls):
        after_school_registration: AfterSchoolRegistration
        for after_school_registration in AfterSchoolRegistration.objects.all().iterator():
            try:
                holder: Holder = Holder.objects.filter(bank_account=after_school_registration.bank_account).get()
                after_school_registration.holder = holder
                after_school_registration.save()
            except Holder.DoesNotExist:
                print('error no holder for that bank account')
            except Holder.MultipleObjectsReturned:
                print('error bank account with two holders')
