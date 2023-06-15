from unittest import mock
from unittest.mock import MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse
from django.test import TestCase
from django.urls import reverse

from ampa_manager.forms import CheckMembersForm


class TestMemberChecker(TestCase):
    URL = reverse('check_members')
    TEMPLATE = 'check_members.html'
    FORM_ACTION = '/ampa/members/check/'

    @mock.patch('ampa_manager.views.check_members.MemberChecker.obtain_checked_file')
    def test_check_members_post_valid_form(self, mock_checker: MagicMock):
        # Arrange
        example_file = SimpleUploadedFile('example.xls', b'file_content', content_type='text/plain')
        mock_checker.return_value = example_file

        # Act
        response = self.client.post(self.URL, data={'file': example_file}, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, FileResponse)

    def test_check_members_get(self):
        # Act
        response = self.client.get(self.URL)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.TEMPLATE)
        self.assertEqual(response.context['form_action'], self.FORM_ACTION)
        self.assertEqual(response.context['excel_template_file_name'], 'templates/plantilla_consultar_socios.xls')
        self.assertEqual(type(response.context['form']), CheckMembersForm)
        self.assertEqual(response.context['form'].data, {})
        self.assertEqual(response.context['form'].errors, {})

    def test_check_members_put(self):
        # Act
        response = self.client.put(self.URL)

        # Assert
        self.assertEqual(response.status_code, 405)
