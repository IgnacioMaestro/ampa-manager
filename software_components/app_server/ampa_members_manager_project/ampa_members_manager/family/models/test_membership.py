from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership


class TestMembership(TestCase):
    def setUp(self):
        self.academic_course: AcademicCourse = baker.make('AcademicCourse')
        ActiveCourse.objects.create(course=self.academic_course)

    def test_str(self):
        family: Family = baker.make('Family')
        academic_course: AcademicCourse = baker.make('AcademicCourse')
        membership: Membership = Membership(family=family, academic_course=academic_course)
        self.assertEqual(str(membership), f'{str(family)}-{str(academic_course)}')

    def test_is_membership_family_no_membership(self):
        family: Family = baker.make('Family')
        self.assertFalse(Membership.is_member_family(family=family))

    def test_is_membership_family_membership(self):
        family: Family = baker.make('Family')
        baker.make('Membership', family=family, academic_course=self.academic_course)
        self.assertTrue(Membership.is_member_family(family=family))

    def test_is_membership_no_membership(self):
        family: Family = baker.make('Family')
        child: Child = baker.make('Child', family=family)
        self.assertFalse(Membership.is_member_child(child=child))

    def test_is_membership_membership(self):
        family: Family = baker.make('Family')
        child: Child = baker.make('Child', family=family)
        baker.make('Membership', family=family, academic_course=self.academic_course)
        self.assertTrue(Membership.is_member_child(child=child))
