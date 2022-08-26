from django import forms
from django.contrib import admin

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration


class ActivityRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'child'):
            self.fields['bank_account'].queryset = BankAccount.objects.filter(owner__family=self.instance.child.family)
        else:
            self.fields['bank_account'].queryset = BankAccount.objects.all()


class ActivityRegistrationAdmin(admin.ModelAdmin):
    list_display = ['activity_period', 'child', 'amount', 'bank_account']
    list_filter = ['activity_period__name', 'amount']
    search_fields = ['child', 'activity_period']
    form = ActivityRegistrationForm


class ActivityRegistrationInline(admin.TabularInline):
    model = ActivityRegistration
    list_display = ['amount', 'activity_period', 'bank_account', 'child']
    extra = 0
