from django.contrib import admin


class FeeAdmin(admin.ModelAdmin):
    list_display = ['academic_course', 'amount']
    ordering = ['-academic_course']
    list_per_page = 25
