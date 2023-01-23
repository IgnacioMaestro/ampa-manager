from django.contrib import admin


class BankBicCodeAdmin(admin.ModelAdmin):
    list_display = ['bic_code', 'bank_code']
    fields = ['bic_code', 'bank_code']
    ordering = ['bic_code']
    search_fields = ['bank_code', 'bic_code']
    list_per_page = 25
