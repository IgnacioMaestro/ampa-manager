from django.contrib import admin


class CustodyImportationAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'filename']
    ordering = ['-created_at']
    list_per_page = 25
