from django.contrib import admin

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.established_course import EstablishedCourse

admin.site.register(AcademicCourse)
admin.site.register(EstablishedCourse)
