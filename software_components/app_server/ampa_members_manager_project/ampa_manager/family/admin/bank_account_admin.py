import codecs
import csv

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy

from ampa_manager.family.admin.filters.bank_account_filters import BankAccountBICCodeFilter
from ampa_manager.family.models.bank_account.bank_account import BankAccount


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['iban', 'swift_bic']
    fields = ['iban', 'swift_bic', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    list_filter = [BankAccountBICCodeFilter]
    search_fields = ['swift_bic', 'iban']
    list_per_page = 25

    # @admin.action(description=gettext_lazy("Export account owners"))
    # def export_owners(self, _, bank_accounts: QuerySet[BankAccount]):
    #     file_name = gettext_lazy('Bank account owners').lower()
    #     headers = {'Content-Disposition': f'attachment; filename="{file_name}.csv"'}
    #     response = HttpResponse(content_type='text/csv', headers=headers)
    #     response.write(codecs.BOM_UTF8)
    #     csv.writer(response, quoting=csv.QUOTE_ALL).writerows(BankAccount.get_csv_fields(bank_accounts))
    #     return response

    @admin.action(description=gettext_lazy("Complete SWIFT/BIC codes"))
    def complete_swift_bic(self, _, bank_accounts: QuerySet[BankAccount]):
        for bank_account in bank_accounts.iterator():
            if bank_account.swift_bic in [None, '']:
                bank_account.complete_swift_bic()
                bank_account.save()

    actions = ['complete_swift_bic']
