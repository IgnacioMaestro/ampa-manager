import io

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from schwifty import IBAN

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.use_cases.importers.members_importer import MembersImporter
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.models.parent import Parent


class TestMembersImporter(TestCase):
    COLUMNS = 21

    @classmethod
    def setUpTestData(cls):
        academic_course = AcademicCourse.objects.create(initial_year=2025)
        ActiveCourse.objects.create(course=academic_course)

    def test_imports_family_children_parents_holder_and_membership(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='1234567890'))

        result = MembersImporter(self.excel_with([self.member_row(iban)])).run()

        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)
        family = Family.objects.get()
        self.assertEqual(family.surnames, 'García López')
        self.assertEqual(family.email, 'familia@correo.test')
        self.assertEqual(Child.objects.count(), 2)
        self.assertEqual(Parent.objects.count(), 2)
        self.assertEqual(family.membership_holder.bank_account.iban, iban)
        self.assertEqual(family.custody_holder, family.membership_holder)
        self.assertEqual(family.after_school_holder, family.membership_holder)
        self.assertEqual(family.camps_holder, family.membership_holder)
        self.assertTrue(Membership.objects.of_family(family).exists())

    def test_row_without_family_email_is_not_imported(self):
        row = self.member_row(str(IBAN.generate('ES', bank_code='2095', account_code='2234567890')))
        row[0] = None

        result = MembersImporter(self.excel_with([row])).run()

        self.assertEqual(result.rows[0].state, Row.STATE_ERROR)
        self.assertEqual(Family.objects.count(), 0)
        self.assertEqual(Membership.objects.count(), 0)

    def test_import_page_shows_template_and_columns(self):
        response = self.client.get(reverse('import_new_members'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Importar nuevos socios')
        self.assertContains(response, 'Familia: correo')
        self.assertContains(response, 'Padre/Madre 1: nombre y apellidos')
        self.assertContains(response, 'Hijo 1: nombre sin apellidos')
        self.assertContains(response, 'plantilla_importar_socios.xlsx')

    def test_simulation_post_shows_data_and_does_not_save_it(self):
        upload = self.uploaded_file(self.excel_with([
            self.member_row(str(IBAN.generate('ES', bank_code='2095', account_code='3234567890'))),
        ]))

        response = self.client.post(reverse('import_new_members'), {'file': upload, 'simulation': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'García López')
        self.assertContains(response, 'No se ha importado nada')
        self.assertEqual(Family.objects.count(), 0)
        self.assertEqual(Membership.objects.count(), 0)

    def test_post_without_file_does_not_import(self):
        response = self.client.post(reverse('import_new_members'), {'simulation': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('result', response.context)
        self.assertEqual(Family.objects.count(), 0)

    @classmethod
    def member_row(cls, iban: str) -> list:
        row = [None] * cls.COLUMNS
        row[0] = 'familia@correo.test'
        row[1] = 'García López'
        row[2] = 'Ana García López'
        row[3] = '695715902'
        row[4] = 'ana@correo.test'
        row[5] = iban
        row[6] = 'Pedro Núñez'
        row[7] = '695715903'
        row[8] = 'pedro@correo.test'
        row[9] = 'Lucía'
        row[10] = 2019
        row[11] = 'LH1'
        row[12] = 'Mario'
        row[13] = 2017
        row[14] = 'LH3'
        return row

    @classmethod
    def excel_with(cls, data_rows: list[list]) -> bytes:
        content = [[None] * cls.COLUMNS, [None] * cls.COLUMNS, *data_rows]
        buffer = io.BytesIO()
        pd.DataFrame(content).to_excel(buffer, index=False, header=False)
        return buffer.getvalue()

    @staticmethod
    def uploaded_file(content: bytes) -> SimpleUploadedFile:
        return SimpleUploadedFile(
            'socios.xlsx', content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
