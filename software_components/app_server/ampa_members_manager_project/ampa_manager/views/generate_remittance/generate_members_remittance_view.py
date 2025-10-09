from typing import Optional

from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.family.models.membership import Membership
from ampa_manager.forms.generate_members_remittance_form import GenerateMembersRemittanceForm


class GenerateMembersRemittanceView(View):
    HTML_TEMPLATE = 'remittance_generators/generate_members_remittance.html'
    VIEW_NAME = 'generate_members_remittance'

    @classmethod
    def get_context(cls, form: Optional[GenerateMembersRemittanceForm] = None) -> dict:
        if not form:
            form = GenerateMembersRemittanceForm(initial=cls.get_form_initial_data())

        active_course = cls.get_active_course()
        last_course = cls.get_last_course()
        return {
            'form': form,
            'view_url': reverse(cls.VIEW_NAME),
            'title': _('Generate members remittance'),
            'active_course': str(active_course),
            'last_course_fee': cls.get_course_fee(last_course),
            'active_course_members_count': cls.get_members_count(active_course),
            'last_course_members_count': cls.get_members_count(last_course),
            'active_course_members_remittance_count': cls.get_course_members_remittance_count(active_course),
            'fee_link': reverse('admin:ampa_manager_fee_changelist'),
            'membership_link': reverse('admin:ampa_manager_membership_changelist'),
            'membership_remittance_link': reverse('admin:ampa_manager_membershipremittance_changelist')
        }

    @classmethod
    def get_form_initial_data(cls):
        return {
            'active_course_fee': cls.get_course_fee(cls.get_active_course()),
        }

    @classmethod
    def get_course_members_remittance_count(cls, course: Optional[AcademicCourse]) -> int:
        if not course:
            return 0
        return MembershipRemittance.objects.filter(course=course).count()

    @classmethod
    def get_members_count(cls, course: Optional[AcademicCourse]) -> int:
        if not course:
            return 0
        return Membership.objects.of_course(course).count()

    @classmethod
    def get_active_course(cls) -> AcademicCourse:
        return ActiveCourse.load()

    @classmethod
    def get_last_course(cls) -> AcademicCourse:
        active_course = cls.get_active_course()
        return AcademicCourse.objects.get(initial_year=active_course.initial_year-1)

    @classmethod
    def get_course_fee(cls, course: Optional[AcademicCourse]) -> int:
        try:
            return Fee.objects.get(academic_course=course).amount
        except Fee.DoesNotExist:
            return 0

    @classmethod
    def get(cls, request):
        return render(request, cls.HTML_TEMPLATE, cls.get_context())

    @classmethod
    def post(cls, request):
        form = GenerateMembersRemittanceForm(request.POST, request.FILES)
        context = cls.get_context(form)

        if form.is_valid():
            cls.create_or_update_active_course_membership_fee(form.cleaned_data['active_course_fee'])
            remittance: MembershipRemittance = cls.generate_active_course_remittance()
            context['remittance_instance_url'] = remittance.get_admin_url()
            context['notify_families_url'] = reverse('notify_members_remittance', args=[remittance.id])

        return render(request, cls.HTML_TEMPLATE, context)

    @classmethod
    def create_or_update_active_course_membership_fee(cls, amount: int):
        active_course = ActiveCourse.load()
        fee, _ = Fee.objects.get_or_create(academic_course=active_course)
        if fee.amount != amount:
            fee.amount = amount
            fee.save()

    @classmethod
    def generate_active_course_remittance(cls) -> Optional[MembershipRemittance]:
        return None
