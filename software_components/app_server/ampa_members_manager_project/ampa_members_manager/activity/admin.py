from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.activity_payable_part import ActivityPayablePart
from ampa_members_manager.charge.use_cases.create_activity_remittance_with_receipts.activity_remittance_with_receipts_creator import \
    ActivityRemittanceWithReceiptsCreator


class RepetitiveActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding']


class UniqueActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding']


class ActivityPayablePartAdmin(admin.ModelAdmin):
    @admin.action(description=_("Create activity remittance"))
    def create_activity_remittance(self, request, payable_parts: QuerySet[ActivityPayablePart]):
        if not ActivityPayablePart.all_same_repetitive_activity(payable_parts=payable_parts):
            message = _("All Single Activities must be from the same repetitive activity")
            return self.message_user(request, message)
        ActivityRemittanceWithReceiptsCreator(payable_parts).create()
        return self.message_user(request=request, message=_("Activity Remittance created"))

    actions = [create_activity_remittance]
