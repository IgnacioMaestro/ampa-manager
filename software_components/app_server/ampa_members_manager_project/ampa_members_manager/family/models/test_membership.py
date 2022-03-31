from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership


class TestMembership(TestCase):
    def test_str(self):
        family: Family = baker.make('Family')
        academic_course: AcademicCourse = baker.make('AcademicCourse')
        membership: Membership = Membership(family=family, academic_course=academic_course)
        self.assertEqual(str(membership), f'{str(family)}-{str(academic_course)}')
