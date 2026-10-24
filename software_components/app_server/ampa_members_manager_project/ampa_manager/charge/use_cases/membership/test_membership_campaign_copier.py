from django.test import TestCase
from django.urls import reverse

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.use_cases.membership.membership_campaign_copier import MembershipCampaignCopier
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership
from ampa_manager.views.membership_campaign.import_last_course_members_view import ImportLastCourseMembersView


class TestMembershipCampaignCopier(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.previous_course = AcademicCourse.objects.create(initial_year=2024)
        cls.active_course = AcademicCourse.objects.create(initial_year=2025)
        ActiveCourse.objects.create(course=cls.active_course)

        cls.renew_family = cls.family_with_membership('García López', 2019, decline_membership=False)
        cls.out_of_school_family = cls.family_with_membership('Martínez Ruiz', 2000, decline_membership=False)
        cls.declined_family = cls.family_with_membership('Sánchez Gil', 2018, decline_membership=True)

    def test_copies_only_families_that_can_renew(self):
        MembershipCampaignCopier.copy_members_from_last_course()

        self.assertTrue(self.has_active_membership(self.renew_family))
        self.assertFalse(self.has_active_membership(self.out_of_school_family))
        self.assertFalse(self.has_active_membership(self.declined_family))
        self.assertEqual(Membership.objects.of_active_course().count(), 1)

    def test_copying_again_does_not_duplicate_the_active_membership(self):
        MembershipCampaignCopier.copy_members_from_last_course()
        MembershipCampaignCopier.copy_members_from_last_course()

        self.assertEqual(Membership.objects.of_family(self.renew_family).count(), 1)

    def test_import_page_shows_renewal_counts(self):
        response = self.client.get(reverse('import_last_course_members'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Importar socios del curso pasado')
        self.assertContains(response, 'Copiar los socios del curso pasado')
        self.assertEqual(response.context['active_course_members_count'], 0)
        self.assertEqual(response.context['last_course_members_count'], 3)
        self.assertEqual(response.context['families_renew_count'], 1)
        self.assertEqual(response.context['families_not_renew_out_of_school_count'], 1)
        self.assertEqual(response.context['families_not_renew_declined_count'], 1)
        self.assertIn('member=renew', response.context['families_renew_url'])
        self.assertIn('member=yes', response.context['active_course_members_url'])
        self.assertIn(
            'academic_course__initial_year=2025',
            ImportLastCourseMembersView.get_active_course_members_url())

    def test_post_copies_last_course_members_and_shows_the_result(self):
        response = self.client.post(reverse('import_last_course_members'), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Socios del año pasado copiados')
        self.assertEqual(response.context['members_active_course'], 1)
        self.assertTrue(response.context['members_copied'])
        self.assertTrue(self.has_active_membership(self.renew_family))
        self.assertFalse(self.has_active_membership(self.declined_family))

    @classmethod
    def family_with_membership(cls, surnames: str, year_of_birth: int, decline_membership: bool) -> Family:
        family = Family.objects.create(surnames=surnames, decline_membership=decline_membership)
        Child.objects.create(name='Alumno', year_of_birth=year_of_birth, family=family)
        Membership.objects.create(family=family, academic_course=cls.previous_course)
        return family

    def has_active_membership(self, family: Family) -> bool:
        return Membership.objects.filter(family=family, academic_course=self.active_course).exists()
