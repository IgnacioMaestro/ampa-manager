from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from ..models.holder.holder import Holder
from ..models.state import State
from ...activity.admin.after_school_admin import AfterSchoolRegistrationInline
from ...activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ...read_only_inline import ReadOnlyTabularInline


class HolderInline(admin.TabularInline):
    model = Holder
    extra = 0


class ReadOnlyHolderInline(ReadOnlyTabularInline):
    model = Holder
    extra = 0


class HolderAdmin(admin.ModelAdmin):
    list_display = ['parent', 'bank_account', 'authorization_full_number', 'authorization_state', 'after_schools_count']
    ordering = ['parent__name_and_surnames']
    list_filter = ['authorization_year', 'authorization_state']
    search_fields = ['parent__name_and_surnames', 'authorization_sign_date',
                     'bank_account__iban', 'parent__name_and_surnames', 'id']
    list_per_page = 25
    inlines = [AfterSchoolRegistrationInline]

    @admin.action(description=_("Set authorization as  not sent"))
    def set_as_not_sent(self, request, queryset: QuerySet[Holder]):
        queryset.update(state=State.NOT_SENT)

        message = _("%(num_authorizations)s authorizations set as NOT sent") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=_("Set authorization as sent"))
    def set_as_sent(self, request, queryset: QuerySet[Holder]):
        queryset.update(state=State.SENT)

        message = _("%(num_authorizations)s authorizations set as sent") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=_("Set authorization as signed"))
    def set_as_signed(self, request, queryset: QuerySet[Holder]):
        queryset.update(state=State.SIGNED)

        message = _("%(num_authorizations)s authorizations set as signed") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_not_sent, set_as_sent, set_as_signed]

    def get_changeform_initial_data(self, request):
        year: int = timezone.now().year
        next_number = Holder.objects.next_order_for_year(year)
        return {'year': year, 'number': str(next_number)}

    @admin.display(description=_('After-schools'))
    def after_schools_count(self, holder):
        return AfterSchoolRegistration.objects.of_holder(holder).count()
