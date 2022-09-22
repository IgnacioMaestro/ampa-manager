from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.use_cases.create_activity_remittance_with_receipts.activity_remittance_with_receipts_creator import \
    ActivityRemittanceWithReceiptsCreator
from ampa_members_manager.activity_registration.admin import ActivityRegistrationInline


class ActivityPeriodAdmin(admin.ModelAdmin):
    @admin.action(description=_("Create activity remittance"))
    def create_activity_remittance(self, request, activity_periods: QuerySet[ActivityPeriod]):
        if not ActivityPeriod.all_same_activity(activity_periods=activity_periods):
            message = _("All period activities must belong to the same activity")
            return self.message_user(request, message)
        ActivityRemittanceWithReceiptsCreator(activity_periods).create()
        return self.message_user(request=request, message=_("Activity remittance created"))

    actions = [create_activity_remittance]
    inlines = [ActivityRegistrationInline]
    list_display = ['activity', 'name', 'price_for_member', 'price_for_no_member', 'payment_type']
    ordering = ['activity', 'name']
    list_filter = ['activity__name', 'payment_type']
    search_fields = ['name']
    list_per_page = 25


class ActivityPeriodInline(admin.TabularInline):
    model = ActivityPeriod
    list_display = ['activity', 'name', 'price_for_member', 'price_for_no_member', 'payment_type']
    ordering = ['activity', 'name']
    extra = 0


class ActivityAdmin(admin.ModelAdmin):
    list_display = ['academic_course', 'name', 'funding']
    ordering = ['-academic_course', 'name']
    list_filter = ['funding', 'academic_course__initial_year']
    inlines = [ActivityPeriodInline]
    search_fields = ['name']
    list_per_page = 25
