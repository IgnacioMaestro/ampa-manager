from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent


class TestFamilyAdmin(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.force_login(user)
        ActiveCourse.objects.create(course=AcademicCourse.objects.create(initial_year=2025))
        self.parent = Parent.objects.create(name_and_surnames='Ana García')

    def test_add_page_loads_for_unsaved_family(self):
        response = self.client.get(reverse('admin:ampa_manager_family_add'))

        self.assertEqual(response.status_code, 200)

    def test_admin_rejects_family_email_outside_required_domain(self):
        DynamicSetting(family_email_domain='@abendanoikastola.com').save()

        response = self.client.post(reverse('admin:ampa_manager_family_add'), {
            'surnames': 'García',
            'email': 'familia@gmail.com',
            'secondary_email': '',
            'parents': [self.parent.id],
            **self.inline_form_data(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '@abendanoikastola.com')
        self.assertEqual(Family.objects.count(), 0)

    def test_admin_change_rejects_secondary_email_outside_required_domain(self):
        DynamicSetting(family_email_domain='@abendanoikastola.com').save()
        family = Family.objects.create(surnames='García', email='familia@abendanoikastola.com')
        family.parents.add(self.parent)

        response = self.client.post(
            reverse('admin:ampa_manager_family_change', args=[family.id]),
            {
                'surnames': 'García',
                'email': 'familia@abendanoikastola.com',
                'secondary_email': 'otro@gmail.com',
                'parents': [self.parent.id],
                **self.inline_form_data(),
            })

        family.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '@abendanoikastola.com')
        self.assertIsNone(family.secondary_email)

    def test_admin_saves_family_email_with_required_domain(self):
        DynamicSetting(family_email_domain='@abendanoikastola.com').save()

        response = self.client.post(reverse('admin:ampa_manager_family_add'), {
            'surnames': 'García',
            'email': 'familia@abendanoikastola.com',
            'secondary_email': 'familia2@abendanoikastola.com',
            'parents': [self.parent.id],
            **self.inline_form_data(),
        })

        family = Family.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(family.email, 'familia@abendanoikastola.com')
        self.assertEqual(family.secondary_email, 'familia2@abendanoikastola.com')

    @staticmethod
    def inline_form_data():
        return {
            'child_set-TOTAL_FORMS': '0',
            'child_set-INITIAL_FORMS': '0',
            'child_set-MIN_NUM_FORMS': '0',
            'child_set-MAX_NUM_FORMS': '0',
            'membership_set-TOTAL_FORMS': '0',
            'membership_set-INITIAL_FORMS': '0',
            'membership_set-MIN_NUM_FORMS': '0',
            'membership_set-MAX_NUM_FORMS': '0',
        }
