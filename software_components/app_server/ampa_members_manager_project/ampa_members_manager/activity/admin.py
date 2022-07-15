from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.use_cases.create_charge_group_with_charges.charge_group_with_charges_creator import \
    ChargeGroupWithChargesCreator


class RepetitiveActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activities']


class UniqueActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activity']


class SingleActivityAdmin(admin.ModelAdmin):
    @admin.action(description=_("Create charge group"))
    def create_charge_group(self, request, single_activities: QuerySet[SingleActivity]):
        if not self.all_same_repetitive_activity(single_activities=single_activities):
            message = _("All Single Activities must be from the same repetitive activity")
            return self.message_user(request, message)
        ChargeGroupWithChargesCreator(single_activities).create()
        return self.message_user(request=request, message=_("Charge group created"))

    def all_same_repetitive_activity(self, single_activities: QuerySet[SingleActivity]) -> bool:
        first_single_activity: SingleActivity = single_activities.first()
        repetitive_activity: RepetitiveActivity = first_single_activity.repetitiveactivity_set.first()
        for single_activity in single_activities.all():
            if single_activity.repetitiveactivity_set.first() != repetitive_activity:
                return False
        return True

    actions = [create_charge_group]
