from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from ampa_manager.activity.models.activity_period import ActivityPeriod
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity_registration.admin import ActivityRegistrationInline
from ampa_manager.charge.use_cases.activity.create_activity_remittance_with_receipts.activity_remittance_with_receipts_creator import \
    ActivityRemittanceWithReceiptsCreator
from ampa_manager.charge.use_cases.after_school.create_after_school_remittance_with_receipts.after_school_remittance_with_receipts_creator import \
    AfterSchoolRemittanceWithReceiptsCreator
from ampa_manager.read_only_inline import ReadOnlyTabularInline


def create_message_with_link(url):
    return mark_safe(
        _("Activity remittance created") + " (<a href=\"" + url + "\">" + _(
            "View details") + "</a>)")


class ActivityPeriodAdmin(admin.ModelAdmin):

    @admin.action(description=_("Create activity remittance"))
    def create_activity_remittance(self, request, activity_periods: QuerySet[ActivityPeriod]):
        remittance = ActivityRemittanceWithReceiptsCreator(activity_periods).create()
        message = create_message_with_link(remittance.get_admin_url())
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


class AfterSchoolRegistrationAdmin(admin.ModelAdmin):
    list_display = ['after_school_edition', 'child', 'bank_account']
    ordering = ['after_school_edition__after_school__name', 'after_school_edition']
    list_filter = ['after_school_edition__after_school__name']
    search_fields = ['child__name', 'after_school_edition__after_school__name']
    list_per_page = 25


class AfterSchoolRegistrationInline(ReadOnlyTabularInline):
    model = AfterSchoolRegistration
    list_display = ['after_school_edition', 'child', 'bank_account']
    ordering = ['after_school_edition__after_school__name', 'after_school_edition']
    extra = 0


class AfterSchoolEditionAdmin(admin.ModelAdmin):
    inlines = [AfterSchoolRegistrationInline]
    list_display = ['after_school', 'price_for_member', 'price_for_no_member', 'academic_course', 'registrations_count']
    ordering = ['-academic_course', 'after_school']
    list_filter = ['after_school__name']
    search_fields = ['after_school__name']
    list_per_page = 25

    @admin.display(description=_('Registrations'))
    def registrations_count(self, after_school_edition):
        return after_school_edition.afterschoolregistration_set.count()

    @admin.action(description=_("Create after school remittance"))
    def create_after_school_remittance(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance = AfterSchoolRemittanceWithReceiptsCreator(after_school_editions).create()
        message = create_message_with_link(after_school_remittance.get_admin_url())
        return self.message_user(request=request, message=message)

    @admin.action(description=_("Create after school remittance with half"))
    def create_after_school_remittance_half(self, request, after_school_editions: QuerySet[AfterSchoolEdition]):
        after_school_remittance = AfterSchoolRemittanceWithReceiptsCreator(after_school_editions).create_with_fraction(0.5)
        message = create_message_with_link(after_school_remittance.get_admin_url())
        return self.message_user(request=request, message=message)

    actions = [create_after_school_remittance, create_after_school_remittance_half]


class AfterSchoolEditionInline(admin.TabularInline):
    model = AfterSchoolEdition
    list_display = ['after_school', 'price_for_member', 'price_for_no_member', 'academic_course']
    ordering = ['-academic_course', 'after_school']
    extra = 0


class AfterSchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'funding', 'after_school_edition_count']
    ordering = ['name']
    list_filter = ['funding']
    inlines = [AfterSchoolEditionInline]
    search_fields = ['name']
    list_per_page = 35

    @admin.display(description=_('Editions'))
    def after_school_edition_count(self, after_school):
        return after_school.afterschooledition_set.count()
