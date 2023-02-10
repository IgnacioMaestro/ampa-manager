from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from ampa_manager.activity.models.activity_period import ActivityPeriod
from ampa_manager.activity_registration.admin import ActivityRegistrationInline
from ampa_manager.charge.use_cases.activity.create_activity_remittance_with_receipts.activity_remittance_with_receipts_creator import \
    ActivityRemittanceWithReceiptsCreator


class ActivityPeriodAdmin(admin.ModelAdmin):

    @admin.action(description=_("Create activity remittance"))
    def create_activity_remittance(self, request, activity_periods: QuerySet[ActivityPeriod]):
        remittance = ActivityRemittanceWithReceiptsCreator(activity_periods).create()
        url = remittance.get_admin_url()
        message = mark_safe(
            _("Activity remittance created") + " (<a href=\"" + url + "\">" + _("View details") + "</a>)")
        return self.message_user(request=request, message=message)

    actions = [create_activity_remittance]
    inlines = [ActivityRegistrationInline]
    list_display = ['activity', 'name', 'price_for_member', 'price_for_no_member', 'registered_count', 'payment_type']
    ordering = ['activity', 'name']
    list_filter = ['activity__name', 'payment_type']
    search_fields = ['name']

    list_per_page = 25

    @admin.display(description=_('Signed up'))
    def registered_count(self, activity_period):
        return activity_period.activityregistration_set.count()


class ActivityPeriodInline(admin.TabularInline):
    model = ActivityPeriod
    list_display = ['activity', 'name', 'price_for_member', 'price_for_no_member', 'payment_type']
    ordering = ['activity', 'name']
    extra = 0


class ActivityAdmin(admin.ModelAdmin):
    list_display = ['academic_course', 'name', 'funding', 'activity_period_count']
    ordering = ['-academic_course', 'name']
    list_filter = ['funding', 'academic_course__initial_year']
    inlines = [ActivityPeriodInline]
    search_fields = ['name']
    list_per_page = 35

    @admin.display(description=_('Periods'))
    def activity_period_count(self, activity):
        return activity.activityperiod_set.count()


