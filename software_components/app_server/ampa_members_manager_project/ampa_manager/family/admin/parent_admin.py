from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.admin.family_admin import FamilyInline
from ampa_manager.family.admin.filters.parent_filters import ParentFamilyEmailsFilter, ParentFamiliesCountFilter
from ampa_manager.family.admin.holder_admin import ReadOnlyHolderInline
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership


class ParentAdmin(admin.ModelAdmin):
    list_display = ['name_and_surnames', 'parent_families', 'email', 'phone_number', 'additional_phone_number',
                    'is_member', 'holders_count']
    fields = ['name_and_surnames', 'phone_number', 'additional_phone_number', 'email', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    ordering = ['name_and_surnames']
    search_fields = ['name_and_surnames', 'family__surnames', 'phone_number', 'email', 'additional_phone_number',
                     'id']
    inlines = [FamilyInline, ReadOnlyHolderInline]
    list_per_page = 25
    list_filter = [ParentFamilyEmailsFilter, ParentFamiliesCountFilter]

    @admin.display(description=_('Is member'))
    def is_member(self, parent):
        return _('Yes') if Membership.objects.of_parent(parent).exists() else _('No')

    @admin.display(description=_('Family'))
    def parent_families(self, parent):
        return ', '.join(str(f) for f in parent.family_set.all())

    @admin.display(description=_('Holders'))
    def holders_count(self, parent):
        return Holder.objects.of_parent(parent).count()
