import csv
from datetime import datetime

from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity.models.unique_activity import UniqueActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.parent import Parent
from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.models.charge import Charge


class RepetitiveActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activities']


class UniqueActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activity']


@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ['summary', 'fee']

    def summary(self, instance):
        return str(instance)


class FamilyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['default_bank_account'].queryset = BankAccount.objects.filter(owner__family=self.instance)


class ChildInline(admin.TabularInline):
    model = Child
    extra = 0

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['first_surname', 'second_surname', 'email', 'default_bank_account']
    search_fields = ['first_surname', 'second_surname', 'email']
    form = FamilyAdminForm
    filter_horizontal = ['parents']
    inlines = [
        ChildInline
    ]

class ActivityRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'child'):
            self.fields['bank_account'].queryset = BankAccount.objects.filter(owner__family=self.instance.child.family)
        else:
            self.fields['bank_account'].queryset = BankAccount.objects.all()

@admin.register(ActivityRegistration)
class ActivityRegistrationAdmin(admin.ModelAdmin):
    form = ActivityRegistrationForm


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 0


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['swift_bic', 'iban', 'owner']
    list_filter = ['swift_bic']
    search_fields = ['swift_bic', 'iban', 'owner']
    inlines = [
        AuthorizationInline
    ]


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['name', 'first_surname', 'second_surname', 'phone_number']
    search_fields = ['name', 'first_surname', 'second_surname', 'phone_number']


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'year_of_birth', 'repetition', 'family']
    list_filter = ['year_of_birth', 'repetition']
    search_fields = ['name', 'year_of_birth', 'repetition', 'family']


@admin.register(Authorization)
class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ['number', 'year', 'bank_account', 'document']
    list_filter = ['year']
    search_fields = ['number', 'year', 'bank_account']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['family', 'academic_course']
    list_filter = ['academic_course']
    search_fields = ['family', 'academic_course']


class ChargeInline(admin.TabularInline):
    model = Charge
    extra = 0


@admin.register(ChargeGroup)
class ChargeGroupAdmin(admin.ModelAdmin):
    inlines = [
        ChargeInline
    ]

    def download_csv(self, request, queryset):
        filename = 'charge_groups_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.csv'

        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            },
        )

        writer = csv.writer(response)
        for charge_group in queryset.all():
            for charge in charge_group.charge_set.all():
                receipt = charge.generate_receipt()
                writer.writerow(receipt.get_csv_properties())

        return response

    download_csv.short_description = _("Export to CSV")

    actions = [download_csv]


admin.site.register(ActiveCourse)
admin.site.register(RepetitiveActivity, RepetitiveActivityAdmin)
admin.site.register(UniqueActivity, UniqueActivityAdmin)
admin.site.register(SingleActivity)
admin.site.register(Charge)
