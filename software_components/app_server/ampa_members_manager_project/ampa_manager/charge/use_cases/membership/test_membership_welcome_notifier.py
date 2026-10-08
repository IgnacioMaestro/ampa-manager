from unittest.mock import patch

from django.conf import settings
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.charge.use_cases.membership.membership_welcome_notifier import MembershipWelcomeNotifier
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership


@override_settings(TEST_EMAIL_RECIPIENT='test@example.com')
class TestMembershipWelcomeNotifier(TestCase):
    def setUp(self):
        self.academic_course: AcademicCourse = baker.make(AcademicCourse)
        ActiveCourse.objects.create(course=self.academic_course)

    @patch('ampa_manager.charge.use_cases.membership.membership_welcome_notifier.Mailer.send_template_mail')
    def test_notify_sends_to_current_course_member_emails(self, send_template_mail):
        family: Family = baker.make(Family, email='member@example.com', secondary_email='member2@example.com')
        baker.make(Membership, family=family, academic_course=self.academic_course)
        other_course: AcademicCourse = baker.make(AcademicCourse)
        other_family: Family = baker.make(Family, email='other@example.com', secondary_email='other2@example.com')
        baker.make(Membership, family=other_family, academic_course=other_course)
        send_template_mail.return_value = MailNotifierResult(success_emails=['member@example.com', 'member2@example.com'])

        result = MembershipWelcomeNotifier().notify()

        send_template_mail.assert_called_once()
        kwargs = send_template_mail.call_args.kwargs
        self.assertEqual(kwargs['bcc_recipients'], ['member@example.com', 'member2@example.com'])
        self.assertEqual(kwargs['subject'], MembershipWelcomeNotifier.MAIL_SUBJECT)
        self.assertEqual(kwargs['body_html_template'], MembershipWelcomeNotifier.MAIL_TEMPLATE)
        self.assertEqual(kwargs['body_html_context'], {
            'course': str(self.academic_course),
            'info_email': settings.INFO_EMAIL,
            'whatsapp_community_url': settings.WHATSAPP_COMMUNITY_URL,
            'website_url': settings.WEBSITE_URL,
            'website_label': settings.WEBSITE_LABEL,
            'committees_url': settings.COMMITTEES_URL,
        })
        html = render_to_string(kwargs['body_html_template'], kwargs['body_html_context'])
        self.assertIn('lista de comisiones', html)
        self.assertIn('batzordeen zerrenda', html)
        self.assertEqual(html.count(f'mailto:{settings.INFO_EMAIL}'), 2)
        self.assertEqual(html.count(f'href="{settings.WHATSAPP_COMMUNITY_URL}"'), 2)
        self.assertEqual(html.count(f'href="{settings.WEBSITE_URL}"'), 2)
        self.assertEqual(html.count(f'href="{settings.COMMITTEES_URL}"'), 2)
        self.assertEqual(html.count(f'>{settings.WEBSITE_LABEL}</a>'), 2)
        self.assertIn(str(self.academic_course), kwargs['body_text_content'])
        self.assertIn(settings.INFO_EMAIL, kwargs['body_text_content'])
        self.assertIn(settings.WHATSAPP_COMMUNITY_URL, kwargs['body_text_content'])
        self.assertIn(settings.WEBSITE_URL, kwargs['body_text_content'])
        self.assertIn(settings.COMMITTEES_URL, kwargs['body_text_content'])
        self.assertEqual(result.success_emails, ['member@example.com', 'member2@example.com'])

    @patch('ampa_manager.charge.use_cases.membership.membership_welcome_notifier.Mailer.send_template_mail')
    def test_notify_deduplicates_emails(self, send_template_mail):
        family: Family = baker.make(Family, email='shared@example.com', secondary_email='shared@example.com')
        baker.make(Membership, family=family, academic_course=self.academic_course)
        other_family: Family = baker.make(Family, email='shared@example.com', secondary_email=None)
        baker.make(Membership, family=other_family, academic_course=self.academic_course)
        send_template_mail.return_value = MailNotifierResult(success_emails=['shared@example.com'])

        MembershipWelcomeNotifier().notify()

        self.assertEqual(send_template_mail.call_args.kwargs['bcc_recipients'], ['shared@example.com'])

    @patch('ampa_manager.charge.use_cases.membership.membership_welcome_notifier.Mailer.send_template_mail')
    def test_notify_without_members_does_not_send(self, send_template_mail):
        result = MembershipWelcomeNotifier().notify()

        send_template_mail.assert_not_called()
        self.assertEqual(result.success_emails, [])
        self.assertIsNone(result.error)

    @patch('ampa_manager.charge.use_cases.membership.membership_welcome_notifier.Mailer.send_template_mail')
    def test_notify_test_sends_only_to_test_recipient(self, send_template_mail):
        family: Family = baker.make(Family, email='member@example.com', secondary_email='member2@example.com')
        baker.make(Membership, family=family, academic_course=self.academic_course)
        send_template_mail.return_value = MailNotifierResult(success_emails=['test@example.com'])

        MembershipWelcomeNotifier(is_a_test=True).notify()

        self.assertEqual(send_template_mail.call_args.kwargs['bcc_recipients'], ['test@example.com'])


@override_settings(TEST_EMAIL_RECIPIENT='test@example.com')
class TestWelcomeMembersView(TestCase):
    def setUp(self):
        academic_course: AcademicCourse = baker.make(AcademicCourse)
        ActiveCourse.objects.create(course=academic_course)
        family: Family = baker.make(Family, email='member@example.com', secondary_email=None)
        baker.make(Membership, family=family, academic_course=academic_course)

    def test_get_shows_current_course_members(self):
        response = self.client.get(reverse('welcome_members'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dar la bienvenida a los socios')
        self.assertContains(response, 'value="1"')
        self.assertContains(response, reverse('notify_members_campaign'))

    @patch('ampa_manager.views.membership_campaign.welcome_members_view.MembershipWelcomeNotifier.notify')
    def test_post_sends_welcome_and_shows_result(self, notify):
        notify.return_value = MailNotifierResult(success_emails=['member@example.com'])

        response = self.client.post(reverse('welcome_members'))

        self.assertEqual(response.status_code, 200)
        notify.assert_called_once()
        self.assertContains(response, 'member@example.com')
