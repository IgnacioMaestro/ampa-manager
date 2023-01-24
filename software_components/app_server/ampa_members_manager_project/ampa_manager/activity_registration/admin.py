from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.read_only_inline import ReadOnlyTabularInline


class ActivityRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'child'):
            self.fields['holder'].queryset = Holder.objects.of_family(self.instance.child.family)
        else:
            self.fields['holder'].queryset = Holder.objects.all()


class ActivityRegistrationAdmin(admin.ModelAdmin):
    list_display = ['activity_name', 'activity_period', 'child', 'amount', 'holder']
    ordering = ['activity_period__activity__name', 'activity_period']
    list_filter = ['activity_period__activity__name', 'activity_period__name', 'amount']
    search_fields = ['child__name', 'activity_period__name']
    list_per_page = 25

    @admin.display(description=_('Activity'))
    def activity_name(self, activity_registration):
        return activity_registration.activity_period.activity.name


class ActivityRegistrationInline(ReadOnlyTabularInline):
    model = ActivityRegistration
    list_display = ['amount', 'activity_period', 'bank_account', 'child']
    ordering = ['activity_period']
    extra = 0
