from django.contrib import admin


class MembershipAdmin(admin.ModelAdmin):
    list_display = ['family', 'academic_course']
    ordering = ['-academic_course', 'family__surnames']
    list_filter = ['academic_course__initial_year']
    search_fields = ['family__surnames', 'academic_course__initial_year']
    list_per_page = 25
