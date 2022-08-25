from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.use_cases.create_activity_remittance_with_receipts.activity_remittance_with_receipts_creator import \
    ActivityRemittanceWithReceiptsCreator


class RepetitiveActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_course', 'funding']
    list_filter = ['academic_course', 'funding']
    search_fields = ['name', 'academic_course']
    fields = ['name', 'academic_course', 'funding']


class ActivityPeriodAdmin(admin.ModelAdmin):
    @admin.action(description=_("Create activity remittance"))
    def create_activity_remittance(self, request, activity_periods: QuerySet[ActivityPeriod]):
        if not ActivityPeriod.all_same_activity(activity_periods=activity_periods):
            message = _("All Single Activities must be from the same repetitive activity")
            return self.message_user(request, message)
        ActivityRemittanceWithReceiptsCreator(activity_periods).create()
        return self.message_user(request=request, message=_("Activity Remittance created"))

    actions = [create_activity_remittance]


class ActivityPeriodInline(admin.TabularInline):
    model = ActivityPeriod
    list_display = ['name', 'price_for_member', 'price_for_no_member', 'payment_type', 'activity']
    extra = 0


class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_course', 'funding']
    list_filter = ['funding', 'academic_course__initial_year']
    inlines = [ActivityPeriodInline]



