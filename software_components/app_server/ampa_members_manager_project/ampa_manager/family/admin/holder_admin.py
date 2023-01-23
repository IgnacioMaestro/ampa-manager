from django.contrib import admin

from ampa_manager.family.models.holder.holder import Holder


class HolderInline(admin.TabularInline):
    model = Holder
    extra = 0


class HolderAdmin(admin.ModelAdmin):
    list_display = ['parent', 'bank_account', 'full_number', 'authorization_state']
    ordering = ['parent__name_and_surnames']
    search_fields = ['parent__name_and_surnames']
    list_per_page = 25
