from django import forms
from django.contrib import admin

from ampa_members_manager.family.models.bank_account import BankAccount


class ActivityRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'child'):
            self.fields['bank_account'].queryset = BankAccount.objects.filter(owner__family=self.instance.child.family)
        else:
            self.fields['bank_account'].queryset = BankAccount.objects.all()


class ActivityRegistrationAdmin(admin.ModelAdmin):
    list_display = ['activity_period', 'child', 'amount', 'bank_account']
    list_filter = ['activity_period', 'amount']
    search_fields = ['child', 'activity_period']
    form = ActivityRegistrationForm
