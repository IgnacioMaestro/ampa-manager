from django.contrib import admin

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.established_course import EstablishedCourse
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.parent import Parent

admin.site.register(AcademicCourse)
admin.site.register(EstablishedCourse)
admin.site.register(Family)
admin.site.register(Child)
admin.site.register(Parent)
admin.site.register(BankAccount)
admin.site.register(Authorization)
