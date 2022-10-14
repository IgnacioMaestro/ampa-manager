from datetime import date

from django.db.models import Q, F, Count
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.family.models.state import State
from ampa_members_manager.academic_course.models.course_name import CourseName


class CourseListFilter(admin.SimpleListFilter):
    title = _('Course')

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        return (
            (CourseName.AGE_HH2, _('HH2')),
            (CourseName.AGE_HH3, _('HH3')),
            (CourseName.AGE_HH4, _('HH4')),
            (CourseName.AGE_HH5, _('HH5')),
            (CourseName.AGE_LH1, _('LH1')),
            (CourseName.AGE_LH2, _('LH2')),
            (CourseName.AGE_LH3, _('LH3')),
            (CourseName.AGE_LH4, _('LH4')),
            (CourseName.AGE_LH5, _('LH5')),
            (CourseName.AGE_LH6, _('LH6')),
        )

    def queryset(self, request, queryset):
        if self.value():
            years_since_birth = int(self.value())
            active_course = ActiveCourse.load()
            default_year_of_birth = active_course.initial_year - years_since_birth

            return queryset.annotate(course=active_course.initial_year - F('year_of_birth') - F('repetition')).filter(course=years_since_birth)
        else:
            return queryset

class CycleFilter(admin.SimpleListFilter):
    title = _('Cycle')

    parameter_name = 'cycle'

    def lookups(self, request, model_admin):
        return (
            ('pre', _('Pre-school')),
            ('pri', _('Primary education')),
            ('out', _('Out of school')),
        )

    def queryset(self, request, queryset):
        if self.value():
            active_course = ActiveCourse.load()

            queryset = queryset.annotate(course=active_course.initial_year - F('year_of_birth') - F('repetition'))

            if self.value() == 'pre':
                return queryset.filter(course__range=(CourseName.AGE_HH2, CourseName.AGE_HH5))
            elif self.value() == 'pri':
                return queryset.filter(course__range=(CourseName.AGE_LH1, CourseName.AGE_LH6))
            elif self.value() == 'out':
                return queryset.filter(Q(course__lt=CourseName.AGE_HH2) | Q(course__gt=CourseName.AGE_LH6))
        else:
            return queryset

class FamilyIsMemberFilter(admin.SimpleListFilter):
    title = _('Membership')

    parameter_name = 'member'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Members')),
            ('no', _('No members')),
        )

    def queryset(self, request, queryset):
        if self.value():
            active_course = ActiveCourse.load()

            if self.value() == 'yes':
                return queryset.filter(membership__academic_course=active_course)
            elif self.value() == 'no':
                return queryset.exclude(membership__academic_course=active_course)
        else:
            return queryset

class FamilyChildrenCountFilter(admin.SimpleListFilter):
    title = _('Children count')

    parameter_name = 'children'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Any children in school')),
            ('no', _('No children in school')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'yes':
                return queryset.has_any_children()
            elif self.value() == 'no':
                return queryset.has_no_children()
        else:
            return queryset

class BankAccountAuthorizationFilter(admin.SimpleListFilter):
    title = _('Authorization')

    parameter_name = 'authorization'

    def lookups(self, request, model_admin):
        return (
            (0, _('No authorization')),
            (State.NOT_SENT, _('Created')),
            (State.SENT, _('Sent')),
            (State.SIGNED, _('Signed')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '0':
                queryset = queryset.annotate(auth_count=Count('authorization'))
                return queryset.filter(auth_count=0)
            else:
                return queryset.filter(authorization__state=self.value())
        else:
            return queryset

class FamilyDefaultAccountFilter(admin.SimpleListFilter):
    title = _('Default account')

    parameter_name = 'account'

    def lookups(self, request, model_admin):
        return (
            ('with', _('With account')),
            ('without', _('Without account')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.exclude(default_bank_account=None)
            elif self.value() == 'without':
                return queryset.filter(default_bank_account=None)
        else:
            return queryset

class BICCodeFilter(admin.SimpleListFilter):
    title = _('SWIFT/BIC')

    parameter_name = 'bic'

    def lookups(self, request, model_admin):
        return (
            ('with', _('With SWIFT/BIC')),
            ('without', _('Without SWIFT/BIC')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'with':
                return queryset.exclude(Q(swift_bic=None) | Q(swift_bic=""))
            elif self.value() == 'without':
                return queryset.filter(Q(swift_bic=None) | Q(swift_bic=""))
        else:
            return queryset