import io

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from schwifty import IBAN

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.family import Family


class TestCustodyImporter(TestCase):
    COLUMNS = 10

    @classmethod
    def setUpTestData(cls):
        cls.course = AcademicCourse.objects.create(initial_year=2025)
        ActiveCourse.objects.create(course=cls.course)
        cls.edition = CustodyEdition.objects.create(
            period='Junio', academic_course=cls.course, cycle=Level.ID_CYCLE_PRIMARY,
            price_for_member='3.50', price_for_no_member='4.50')

    def test_imports_registration_with_assisted_days(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='1234567890'))

        result = CustodyImporter(self.excel_with([self.registration_row(iban, 4)]), self.edition).run()

        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)
        registration = CustodyRegistration.objects.get()
        self.assertEqual(registration.custody_edition, self.edition)
        self.assertEqual(registration.assisted_days, 4)
        self.assertEqual(registration.child.name, 'Lucía')
        family = Family.objects.get()
        self.assertEqual(family.custody_holder, registration.holder)
        self.assertEqual(registration.holder.bank_account.iban, iban)

    def test_row_without_assisted_days_is_not_registered(self):
        row = self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='2234567890')), None)

        result = CustodyImporter(self.excel_with([row]), self.edition).run()

        self.assertEqual(result.rows[0].state, Row.STATE_ERROR)
        self.assertEqual(CustodyRegistration.objects.count(), 0)

    def test_importing_again_updates_assisted_days_without_duplicating(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='3234567890'))

        CustodyImporter(self.excel_with([self.registration_row(iban, 4)]), self.edition).run()
        result = CustodyImporter(self.excel_with([self.registration_row(iban, 6)]), self.edition).run()

        registration = CustodyRegistration.objects.get()
        self.assertEqual(registration.assisted_days, 6)
        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)

    def test_import_page_shows_current_edition_and_columns(self):
        response = self.client.get(reverse('import_custody'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Importar custodia')
        self.assertContains(response, 'Edición de custodia a la que importar')
        self.assertContains(response, 'Días asistidos en la edición seleccionada')
        self.assertContains(response, 'plantilla_importar_ludoteca.xlsx')
        self.assertContains(response, str(self.edition))

    def test_simulation_post_shows_data_and_does_not_save_it(self):
        upload = self.uploaded_file(self.excel_with([
            self.registration_row(str(IBAN.generate('ES', bank_code='2095', account_code='4234567890')), 4),
        ]))

        response = self.client.post(reverse('import_custody'), {
            'file': upload,
            'simulation': 'on',
            'custody_edition': self.edition.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lucía')
        self.assertContains(response, 'No se ha importado nada')
        self.assertEqual(CustodyRegistration.objects.count(), 0)
        self.assertEqual(Family.objects.count(), 0)

    def test_post_without_file_does_not_import(self):
        response = self.client.post(reverse('import_custody'), {
            'simulation': 'on',
            'custody_edition': self.edition.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('result', response.context)
        self.assertEqual(CustodyRegistration.objects.count(), 0)

    @staticmethod
    def registration_row(iban: str, assisted_days) -> list:
        return [
            'familia@correo.test', 'Ana García López', '695715902', 'ana@correo.test', iban,
            'Lucía', 'García López', 2019, 'LH1', assisted_days,
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
            'ludoteca.xlsx', content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
