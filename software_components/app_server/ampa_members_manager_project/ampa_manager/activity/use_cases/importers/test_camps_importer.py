import io

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from schwifty import IBAN

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.use_cases.importers.camps_importer import CampsImporter
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family


class TestCampsImporter(TestCase):
    COLUMNS = 9

    @classmethod
    def setUpTestData(cls):
        cls.course = AcademicCourse.objects.create(initial_year=2025)
        ActiveCourse.objects.create(course=cls.course)
        cls.edition = CampsEdition.objects.create(
            academic_course=cls.course, levels='LH1-LH6',
            price_for_member='80.00', price_for_no_member='100.00')

    def test_imports_registration_for_the_selected_edition(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='1234567890'))

        result = CampsImporter(self.excel_with([self.registration_row(iban)]), self.edition).run()

        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)
        registration = CampsRegistration.objects.get()
        self.assertEqual(registration.camps_edition, self.edition)
        self.assertEqual(registration.child.name, 'Lucía')
        family = Family.objects.get()
        self.assertEqual(family.camps_holder, registration.holder)
        self.assertEqual(registration.holder.bank_account.iban, iban)

    def test_row_without_child_is_not_registered(self):
        row = self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='2234567890')))
        row[5] = None

        result = CampsImporter(self.excel_with([row]), self.edition).run()

        self.assertEqual(result.rows[0].state, Row.STATE_ERROR)
        self.assertEqual(CampsRegistration.objects.count(), 0)
        self.assertEqual(Child.objects.count(), 0)

    def test_importing_the_same_registration_again_does_not_duplicate_it(self):
        content = self.excel_with([
            self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='3234567890'))),
        ])

        CampsImporter(content, self.edition).run()
        result = CampsImporter(content, self.edition).run()

        self.assertEqual(CampsRegistration.objects.count(), 1)
        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)

    def test_import_page_shows_edition_and_columns(self):
        response = self.client.get(reverse('import_camps'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Importar campamentos')
        self.assertContains(response, 'Edición de campamentos a la que importar')
        self.assertContains(response, 'Hijo 1: nombre sin apellidos')
        self.assertContains(response, 'plantilla_importar_campamentos.xlsx')
        self.assertContains(response, str(self.edition))

    def test_simulation_post_shows_data_and_does_not_save_it(self):
        upload = self.uploaded_file(self.excel_with([
            self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='4234567890'))),
        ]))

        response = self.client.post(reverse('import_camps'), {
            'file': upload,
            'simulation': 'on',
            'camps_edition': self.edition.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lucía')
        self.assertContains(response, 'No se ha importado nada')
        self.assertEqual(CampsRegistration.objects.count(), 0)
        self.assertEqual(Family.objects.count(), 0)

    def test_post_without_file_does_not_import(self):
        response = self.client.post(reverse('import_camps'), {
            'simulation': 'on',
            'camps_edition': self.edition.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('result', response.context)
        self.assertEqual(CampsRegistration.objects.count(), 0)

    @staticmethod
    def registration_row(iban: str) -> list:
        return [
            'familia@correo.test', 'Ana García López', '695715902', 'ana@correo.test', iban,
            'Lucía', 'García López', 2019, 'LH1',
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
            'campamentos.xlsx', content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
