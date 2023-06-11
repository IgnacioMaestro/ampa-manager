from unittest import mock
from unittest.mock import MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from ampa_manager.family.use_cases.importers.members_importer import MembersImporter
from ampa_manager.forms import ImportMembersForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns
from ampa_manager.utils.excel.titled_list import TitledList
from ampa_manager.views.import_info import ImportInfo


class ImportMembersViewTest(TestCase):
    URL = reverse('import_members')
    TEMPLATE = 'import_members.html'
    FORM_ACTION = '/ampa/members/import/'

    @mock.patch('ampa_manager.family.use_cases.importers.members_importer.MembersImporter.import_members')
    def test_import_members_post_valid_form(self, mock_import_members: MagicMock):
        # Arrange

        titled_list_summary = TitledList('summary')
        titled_list_results = TitledList('results')
        mock_import_members.return_value = ImportInfo(1, 1, titled_list_summary, titled_list_results)
        example_file = SimpleUploadedFile('example.xls', b'file_content', content_type='text/plain')
        form_data_correct = {'file': example_file}

        # Act
        response = self.client.post(self.URL, data=form_data_correct, follow=True)

        # Assert
        self.assert_200_and_template(response)
        self.assertTrue(response.context['success'])
        self.assertEqual(response.context['import_results'], titled_list_results)
        self.assertEqual(response.context['import_summary'], titled_list_summary)
        self.assertEqual(response.context['excel_columns'], get_excel_columns(MembersImporter.COLUMNS_TO_IMPORT))
        self.assertEqual(response.context['form_action'], self.FORM_ACTION)
        self.assertEqual(type(response.context['form']), ImportMembersForm)
        self.assertEqual(response.context['form'].data, {})
        self.assertEqual(response.context['form'].files['file'].name, example_file.name)
        self.assertEqual(response.context['form'].errors, {})

    def test_import_members_post_invalid_form(self):
        # Act
        response = self.client.post(self.URL, data={}, follow=True)

        # Assert
        self.assert_200_and_template(response)
        self.assert_context_common_data(response)
        self.assertEqual(type(response.context['form']), ImportMembersForm)
        self.assertEqual(response.context['form'].data, {})
        self.assertEqual(len(response.context['form'].errors), 1)
        self.assertEqual(response.context['form'].errors['file'], ['Este campo es obligatorio.'])

    def test_import_members_get(self):
        # Act
        response = self.client.get(self.URL)

        # Assert
        self.assert_200_and_template(response)
        self.assert_context_common_data(response)
        self.assertEqual(type(response.context['form']), ImportMembersForm)
        self.assertEqual(response.context['form'].data, {})
        self.assertEqual(response.context['form'].errors, {})

    def test_import_members_put(self):
        # Act
        response = self.client.put(self.URL)

        # Assert
        self.assertEqual(response.status_code, 405)

    def assert_200_and_template(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.TEMPLATE)

    def assert_context_common_data(self, response):
        self.assertFalse('success' in response.context)
        self.assertFalse('import_results' in response.context)
        self.assertFalse('import_summary' in response.context)
        self.assertEqual(response.context['excel_columns'], get_excel_columns(MembersImporter.COLUMNS_TO_IMPORT))
        self.assertEqual(response.context['form_action'], self.FORM_ACTION)
