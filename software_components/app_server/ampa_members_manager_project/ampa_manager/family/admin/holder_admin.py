from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _, gettext_lazy
from django.utils import timezone

from ..models.holder.holder import Holder
from ..models.state import State
from ...activity.admin.after_school_admin import AfterSchoolRegistrationInline
from ...activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ...charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ...charge.models.camps.camps_receipt import CampsReceipt
from ...charge.models.custody.custody_receipt import CustodyReceipt
from ...read_only_inline import ReadOnlyTabularInline
from ...utils.utils import Utils


class HolderInline(admin.TabularInline):
    model = Holder
    extra = 0


class ReadOnlyHolderInline(ReadOnlyTabularInline):
    model = Holder
    extra = 0
    fields = ['parent', 'bank_account', 'custody_receipts', 'after_school_receipts', 'camps_receipts']
    readonly_fields = fields

    @admin.display(description=gettext_lazy('Custody receipts'))
    def custody_receipts(self, holder):
        return HolderAdmin.get_receipts_link(holder, CustodyReceipt)

    @admin.display(description=gettext_lazy('Custody receipts'))
    def camps_receipts(self, holder):
        return HolderAdmin.get_receipts_link(holder, CampsReceipt)

    @admin.display(description=gettext_lazy('Custody receipts'))
    def after_school_receipts(self, holder):
        return HolderAdmin.get_receipts_link(holder, AfterSchoolReceipt)


class HolderAdmin(admin.ModelAdmin):
    list_display = ['parent', 'bank_account', 'custody_receipts',
                    'after_school_receipts', 'camps_receipts']
    ordering = ['parent__name_and_surnames']
    list_filter = ['authorization_year', 'authorization_state']
    search_fields = ['parent__name_and_surnames', 'authorization_sign_date',
                     'bank_account__iban', 'parent__name_and_surnames', 'id']
    autocomplete_fields = ['parent', 'bank_account']
    list_per_page = 25
    inlines = [AfterSchoolRegistrationInline]

    @classmethod
    def get_receipts_link(cls, holder, receipts_model):
        receipts_count = receipts_model.objects.of_parent(holder.parent).count()
        if receipts_count == 1:
            link_text = gettext_lazy('%(num_receipts)s receipt') % {'num_receipts': receipts_count}
        else:
            link_text = gettext_lazy('%(num_receipts)s receipts') % {'num_receipts': receipts_count}
        filters = f'parent={holder.parent.id}'
        return Utils.get_model_link(model_name=receipts_model.__name__.lower(), link_text=link_text, filters=filters)

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

    @admin.display(description=gettext_lazy('Custody receipts'))
    def custody_receipts(self, holder):
        return HolderAdmin.get_receipts_link(holder, CustodyReceipt)

    @admin.display(description=gettext_lazy('Custody receipts'))
    def camps_receipts(self, holder):
        return HolderAdmin.get_receipts_link(holder, CampsReceipt)

    @admin.display(description=gettext_lazy('Custody receipts'))
    def after_school_receipts(self, holder):
        return HolderAdmin.get_receipts_link(holder, AfterSchoolReceipt)
