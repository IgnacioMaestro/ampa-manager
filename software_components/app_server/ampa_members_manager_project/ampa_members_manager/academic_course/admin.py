from django.contrib import admin


class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ['summary', 'fee']

    @staticmethod
    def summary(instance):
        return str(instance)
