from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy

from ampa_manager.family.admin.filters.bank_account_filters import BankAccountBICCodeFilter
from ampa_manager.family.admin.holder_admin import HolderInline
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.holder.holder import Holder


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['iban', 'swift_bic', 'holders_count']
    fields = ['iban', 'swift_bic', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    list_filter = [BankAccountBICCodeFilter]
    search_fields = ['swift_bic', 'iban']
    list_per_page = 25
    inlines = [HolderInline]

    @admin.display(description=_('Holders'))
    def holders_count(self, bank_account):
        return Holder.objects.of_bank_account(bank_account).count()

    @admin.action(description=gettext_lazy("Complete SWIFT/BIC codes"))
    def complete_swift_bic(self, _, bank_accounts: QuerySet[BankAccount]):
        for bank_account in bank_accounts.iterator():
            if bank_account.swift_bic in [None, '']:
                bank_account.complete_swift_bic()
                bank_account.save()

    @admin.action(description=gettext_lazy("Validate IBAN"))
    def validate_iban(self, request, bank_accounts: QuerySet[BankAccount]):
        not_valid_bank_accounts = []
        for bank_account in bank_accounts.iterator():
            if not BankAccount.iban_is_valid(str(bank_account.iban)):
                not_valid_bank_accounts.append(str(bank_account.iban))

        if len(not_valid_bank_accounts) == 0:
            return self.message_user(request=request, message=_('All validated IBANs are valid'))
        else:
            return self.message_user(request=request, message=_('%(number)s IBANs are invalid: %(ibans)s') %
                                                              {'number': len(not_valid_bank_accounts),
                                                               'ibans': ', '.join(not_valid_bank_accounts)})

    actions = ['complete_swift_bic', 'validate_iban']
