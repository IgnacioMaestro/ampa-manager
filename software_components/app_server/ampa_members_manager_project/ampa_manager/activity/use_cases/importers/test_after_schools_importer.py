import io

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from schwifty import IBAN

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.funding import Funding
from ampa_manager.activity.use_cases.importers.after_schools_importer import AfterSchoolsImporter
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family


class TestAfterSchoolsImporter(TestCase):
    COLUMNS = 10

    @classmethod
    def setUpTestData(cls):
        cls.course = AcademicCourse.objects.create(initial_year=2025)
        ActiveCourse.objects.create(course=cls.course)
        activity = AfterSchool.objects.create(name='Esku', funding=Funding.NO_FUNDING)
        cls.edition = AfterSchoolEdition.objects.create(
            after_school=activity, academic_course=cls.course, code='ESKU-AST-13', period='Viernes',
            timetable='17:00-18:00', price_for_member='45.00', price_for_no_member='60.00')

    def test_imports_registration_for_an_existing_edition(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='1234567890'))

        result = AfterSchoolsImporter(self.excel_with([self.registration_row(iban)])).run()

        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)
        registration = AfterSchoolRegistration.objects.get()
        self.assertEqual(registration.after_school_edition, self.edition)
        self.assertEqual(registration.child.name, 'Lucía')
        family = Family.objects.get()
        self.assertEqual(family.after_school_holder, registration.holder)
        self.assertEqual(registration.holder.bank_account.iban, iban)

    def test_unknown_edition_does_not_create_a_registration(self):
        row = self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='2234567890')))
        row[9] = 'NO-EXISTE'

        result = AfterSchoolsImporter(self.excel_with([row])).run()

        self.assertEqual(result.rows[0].state, Row.STATE_ERROR)
        self.assertEqual(AfterSchoolRegistration.objects.count(), 0)

    def test_importing_the_same_registration_again_does_not_duplicate_it(self):
        content = self.excel_with([
            self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='3234567890'))),
        ])

        AfterSchoolsImporter(content).run()
        result = AfterSchoolsImporter(content).run()

        self.assertEqual(AfterSchoolRegistration.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)

    def test_import_page_shows_template_and_columns(self):
        response = self.client.get(reverse('import_after_schools_registrations'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Importar inscripciones de extraescolares')
        self.assertContains(response, 'Familia: correo')
        self.assertContains(response, 'Código de la edición (ESKU-AST-13)')
        self.assertContains(response, 'plantilla_importar_extraescolares.xlsx')

    def test_simulation_post_shows_data_and_does_not_save_it(self):
        upload = self.uploaded_file(self.excel_with([
            self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='4234567890'))),
        ]))

        response = self.client.post(
            reverse('import_after_schools_registrations'), {'file': upload, 'simulation': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lucía')
        self.assertContains(response, 'No se ha importado nada')
        self.assertEqual(AfterSchoolRegistration.objects.count(), 0)
        self.assertEqual(Family.objects.count(), 0)

    def test_post_without_file_does_not_import(self):
        response = self.client.post(reverse('import_after_schools_registrations'), {'simulation': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('result', response.context)
        self.assertEqual(AfterSchoolRegistration.objects.count(), 0)

    @classmethod
    def registration_row(cls, iban: str) -> list:
        return [
            'familia@correo.test', 'Ana García López', '695715902', 'ana@correo.test', iban,
            'Lucía', 'García López', 2019, 'LH1', 'ESKU-AST-13',
        ]

    @classmethod
    def excel_with(cls, data_rows: list[list]) -> bytes:
        content = [[None] * cls.COLUMNS, [None] * cls.COLUMNS, *data_rows]
        buffer = io.BytesIO()
        pd.DataFrame(content).to_excel(buffer, index=False, header=False)
        return buffer.getvalue()

    @staticmethod
    def uploaded_file(content: bytes) -> SimpleUploadedFile:
        return SimpleUploadedFile(
            'extraescolares.xlsx', content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
