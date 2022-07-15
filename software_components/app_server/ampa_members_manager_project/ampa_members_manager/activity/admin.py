from django.contrib import admin


class RepetitiveActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activities']


class UniqueActivityAdmin(admin.ModelAdmin):
    fields = ['name', 'academic_course', 'funding', 'single_activity']
