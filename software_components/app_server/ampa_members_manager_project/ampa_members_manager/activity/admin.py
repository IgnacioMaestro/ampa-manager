from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.use_cases.create_charge_group_with_charges.charge_group_with_charges_creator import \
    ChargeGroupWithChargesCreator


class RepetitiveActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activities']


class UniqueActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activity']


class SingleActivityAdmin(admin.ModelAdmin):
    @admin.action(description=_("Create charge group"))
    def create_charge_group(self, request, queryset: QuerySet[SingleActivity]):
        ChargeGroupWithChargesCreator(queryset).create()
        return self.message_user(request=request, message=_("Charge group created"))

    actions = [create_charge_group]
