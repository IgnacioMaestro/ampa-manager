import io
from decimal import Decimal

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.funding import Funding
from ampa_manager.activity.use_cases.importers.after_school_activities_importer import AfterSchoolsActivitiesImporter
from ampa_manager.activity.use_cases.importers.row import Row


class TestAfterSchoolsActivitiesImporter(TestCase):
    COLUMNS = 7

    @classmethod
    def setUpTestData(cls):
        cls.course = AcademicCourse.objects.create(initial_year=2025)
        ActiveCourse.objects.create(course=cls.course)

    def test_creates_activity_and_edition(self):
        result = AfterSchoolsActivitiesImporter(self.excel_with([self.activity_row()])).run()

        self.assertEqual(result.rows[0].state, Row.STATE_OK)
        activity = AfterSchool.objects.get()
        self.assertEqual(activity.name, 'Esku')
        self.assertEqual(activity.funding, Funding.NO_FUNDING)
        edition = AfterSchoolEdition.objects.get()
        self.assertEqual(edition.after_school, activity)
        self.assertEqual(edition.academic_course, self.course)
        self.assertEqual(edition.code, 'ESKU-AST-13')
        self.assertEqual(edition.period, 'Viernes')
        self.assertEqual(edition.timetable, '17:00-18:00')
        self.assertEqual(edition.price_for_member, Decimal('45.00'))
        self.assertEqual(edition.price_for_no_member, Decimal('60.00'))

    def test_updates_prices_of_an_existing_edition(self):
        activity = AfterSchool.objects.create(name='Esku', funding=Funding.NO_FUNDING)
        edition = AfterSchoolEdition.objects.create(
            after_school=activity, academic_course=self.course, code='ESKU-AST-13', period='Viernes',
            timetable='17:00-18:00', price_for_member='45.00', price_for_no_member='60.00')
        row = self.activity_row()
        row[5] = 50
        row[6] = 70

        result = AfterSchoolsActivitiesImporter(self.excel_with([row])).run()

        edition.refresh_from_db()
        self.assertEqual(result.rows[0].state, Row.STATE_OK)
        self.assertEqual(AfterSchool.objects.count(), 1)
        self.assertEqual(AfterSchoolEdition.objects.count(), 1)
        self.assertEqual(edition.price_for_member, Decimal('50.00'))
        self.assertEqual(edition.price_for_no_member, Decimal('70.00'))

    def test_row_without_activity_name_is_not_imported(self):
        row = self.activity_row()
        row[0] = None

        result = AfterSchoolsActivitiesImporter(self.excel_with([row])).run()

        self.assertEqual(result.rows[0].state, Row.STATE_ERROR)
        self.assertEqual(AfterSchool.objects.count(), 0)
        self.assertEqual(AfterSchoolEdition.objects.count(), 0)

    def test_import_page_shows_template_and_columns(self):
        response = self.client.get(reverse('import_after_schools_activities'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Importar actividades de extraescolares')
        self.assertContains(response, 'Nombre de la actividad')
        self.assertContains(response, 'Horario de la edición (17:00-18:00)')
        self.assertContains(response, 'Precio de la edición para socios')
        self.assertContains(response, 'plantilla_importar_extraescolares.xlsx')

    def test_simulation_post_shows_data_and_does_not_save_it(self):
        upload = self.uploaded_file(self.excel_with([self.activity_row()]))

        response = self.client.post(
            reverse('import_after_schools_activities'), {'file': upload, 'simulation': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Esku')
        self.assertContains(response, 'No se ha importado nada')
        self.assertEqual(AfterSchool.objects.count(), 0)
        self.assertEqual(AfterSchoolEdition.objects.count(), 0)

    def test_post_without_file_does_not_import(self):
        response = self.client.post(reverse('import_after_schools_activities'), {'simulation': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('result', response.context)
        self.assertEqual(AfterSchool.objects.count(), 0)

    @staticmethod
    def activity_row() -> list:
        return ['Esku', 'ESKU-AST-13', 'Viernes', '17:00-18:00', 'LH1, LH2', 45, 60]

    @classmethod
    def excel_with(cls, data_rows: list[list]) -> bytes:
        content = [[None] * cls.COLUMNS, [None] * cls.COLUMNS, *data_rows]
        buffer = io.BytesIO()
        pd.DataFrame(content).to_excel(buffer, index=False, header=False)
        return buffer.getvalue()

    @staticmethod
    def uploaded_file(content: bytes) -> SimpleUploadedFile:
        return SimpleUploadedFile(
            'actividades.xlsx', content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
