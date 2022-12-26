from django.contrib import admin
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.authorization.authorization import Authorization
from ampa_manager.family.models.state import State


class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ['number', 'year', 'order', 'sign_date', 'bank_account', 'document', 'state']
    ordering = ['-sign_date']
    list_filter = ['year', 'state']
    search_fields = ['number', 'year', 'sign_date', 'bank_account__iban', 'bank_account__owner__name_and_surnames']
    list_per_page = 25

    @admin.action(description=_("Set as not sent"))
    def set_as_not_sent(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.NOT_SENT)

        message = _("%(num_authorizations)s authorizations set as NOT sent") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=_("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.SENT)

        message = _("%(num_authorizations)s authorizations set as sent") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=_("Set as signed"))
    def set_as_signed(self, request, queryset: QuerySet[Authorization]):
        queryset.update(state=State.SIGNED)

        message = _("%(num_authorizations)s authorizations set as signed") % {'num_authorizations': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_not_sent, set_as_sent, set_as_signed]

    def get_changeform_initial_data(self, request):
        year: int = timezone.now().year
        next_number = Authorization.objects.next_order_for_year(year)
        return {'year': year, 'number': str(next_number)}
