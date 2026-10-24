import io

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from schwifty import IBAN

from django.core.exceptions import ValidationError

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.use_cases.importers.family_accounts_importer import FamilyAccountsImporter


class TestFamilyAccountsImporter(TestCase):
    @classmethod
    def setUpTestData(cls):
        academic_course = AcademicCourse.objects.create(initial_year=2025)
        ActiveCourse.objects.create(course=academic_course)

    def test_imports_family_parent_account_and_holder_and_ignores_children(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='1234567890'))
        result = FamilyAccountsImporter(self.excel_with([
            ['familia@correo.test', 'García', 'López', iban, 'Ana García López',
             'Lucía', 'Mario', None, None, 'ana@correo.test', '695715902'],
        ])).run()

        self.assertEqual(result.state, Row.STATE_WARNING)
        self.assertEqual(Child.objects.count(), 0)
        family = Family.objects.get()
        self.assertEqual(family.surnames, 'García López')
        self.assertEqual(family.email, 'familia@correo.test')
        parent = Parent.objects.get()
        self.assertEqual(parent.name_and_surnames, 'Ana García López')
        self.assertEqual(parent.email, 'ana@correo.test')
        self.assertTrue(family.parents.filter(id=parent.id).exists())
        self.assertEqual(BankAccount.objects.get().iban, iban)
        self.assertEqual(family.membership_holder, Holder.objects.get())
        self.assertEqual(family.custody_holder, family.membership_holder)
        self.assertIn(family, [imported.instance for imported in result.rows[0].imported_models_results])

    def test_updates_only_provided_surname_and_keeps_existing_parent_phone(self):
        family = Family.objects.create(surnames='García López', email='familia@correo.test')
        parent = Parent.objects.create(name_and_surnames='Ana García López', phone_number='+34695715902')
        family.parents.add(parent)

        result = FamilyAccountsImporter(self.excel_with([
            ['familia@correo.test', 'Martínez', None, None, 'Ana García López',
             None, None, None, None, None, None],
        ])).run()

        family.refresh_from_db()
        parent.refresh_from_db()
        self.assertEqual(family.surnames, 'Martínez López')
        self.assertEqual(family.email, 'familia@correo.test')
        self.assertEqual(parent.phone_number.as_e164, '+34695715902')
        self.assertIsNone(family.membership_holder)
        self.assertEqual(result.rows[0].state, Row.STATE_OK)
        family_result = self.family_result(result.rows[0])
        self.assertEqual(family_result.state, ImportModelResult.UPDATED)

    def test_assigns_new_email_without_replacing_two_existing_emails(self):
        family = Family.objects.create(
            surnames='García López', email='uno@correo.test', secondary_email='dos@correo.test')

        result = FamilyAccountsImporter(self.excel_with([
            ['tres@correo.test', 'García', 'López', None, None, None, None, None, None, None, None],
        ])).run()

        family.refresh_from_db()
        self.assertEqual(family.email, 'uno@correo.test')
        self.assertEqual(family.secondary_email, 'dos@correo.test')
        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)

    def test_sets_secondary_email_when_primary_is_already_filled(self):
        family = Family.objects.create(surnames='García López', email='uno@correo.test')

        FamilyAccountsImporter(self.excel_with([
            ['dos@correo.test', 'García', 'López', None, None, None, None, None, None, None, None],
        ])).run()

        family.refresh_from_db()
        self.assertEqual(family.email, 'uno@correo.test')
        self.assertEqual(family.secondary_email, 'dos@correo.test')

    def test_iban_without_holder_name_creates_account_and_no_holder(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='2234567890'))

        result = FamilyAccountsImporter(self.excel_with([
            ['familia@correo.test', 'García', 'López', iban, None, None, None, None, None, 'ana@correo.test', None],
        ])).run()

        self.assertEqual(Parent.objects.count(), 0)
        self.assertEqual(Holder.objects.count(), 0)
        self.assertEqual(BankAccount.objects.get().iban, iban)
        self.assertEqual(result.rows[0].state, Row.STATE_WARNING)

    def test_import_page_shows_preview_form_and_ignores_children_columns(self):
        response = self.client.get(reverse('import_family_accounts'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Importar cuentas familiares')
        self.assertContains(response, 'Familia: primer apellido')
        self.assertContains(response, 'Titular: nombre y apellidos')
        self.assertContains(response, 'Las columnas F, G, H e I (nombres de los hijos) se ignoran')
        self.assertContains(response, 'plantilla_importar_correos_de_familias.xlsx')

    def test_simulation_post_shows_loaded_data_and_does_not_save_it(self):
        iban = str(IBAN.generate('ES', bank_code='2095', account_code='3234567890'))
        upload = SimpleUploadedFile(
            'cuentas.xlsx',
            self.excel_with([
                ['familia@correo.test', 'García', 'López', iban, 'Ana García López',
                 'Lucía', None, None, None, 'ana@correo.test', '695715902'],
            ]),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        response = self.client.post(reverse('import_family_accounts'), {'file': upload, 'simulation': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'García López')
        self.assertContains(response, 'No se ha importado nada')
        self.assertEqual(Family.objects.count(), 0)
        self.assertEqual(Child.objects.count(), 0)

    def test_family_email_from_another_domain_is_not_imported(self):
        DynamicSetting(family_email_domain='AbendanoIkastola.com').save()

        result = FamilyAccountsImporter(self.excel_with([
            ['familia@correo.test', 'García', 'López', None, 'Ana García',
             None, None, None, None, 'ana@gmail.com', None],
        ])).run()

        self.assertEqual(Family.objects.count(), 0)
        self.assertEqual(Parent.objects.count(), 0)
        self.assertEqual(result.rows[0].state, Row.STATE_ERROR)
        self.assertIn('@abendanoikastola.com', result.rows[0].columns['family_email'].error)

    def test_family_email_with_required_domain_keeps_holder_email_free(self):
        DynamicSetting(family_email_domain='@AbendanoIkastola.com').save()

        result = FamilyAccountsImporter(self.excel_with([
            ['familia@abendanoikastola.com', 'García', 'López', None, 'Ana García',
             None, None, None, None, 'ana@gmail.com', None],
        ])).run()

        self.assertNotEqual(result.rows[0].state, Row.STATE_ERROR)
        self.assertEqual(Family.objects.get().email, 'familia@abendanoikastola.com')
        self.assertEqual(Parent.objects.get().email, 'ana@gmail.com')
        self.assertEqual(DynamicSetting.load().family_email_domain, '@abendanoikastola.com')

    def test_invalid_family_email_domain_is_rejected(self):
        setting = DynamicSetting(family_email_domain='correo')

        with self.assertRaises(ValidationError):
            setting.clean()

    def test_row_without_family_email_or_surnames_is_not_imported(self):
        result = FamilyAccountsImporter(self.excel_with([
            [None, None, None, None, 'Ana García López', None, None, None, None, None, None],
        ])).run()

        self.assertEqual(Family.objects.count(), 0)
        self.assertEqual(Parent.objects.count(), 0)
        self.assertEqual(result.rows[0].state, Row.STATE_ERROR)

    @staticmethod
    def excel_with(data_rows: list[list]) -> bytes:
        content = [[None] * 11, [None] * 11, *data_rows]
        buffer = io.BytesIO()
        pd.DataFrame(content).to_excel(buffer, index=False, header=False)
        return buffer.getvalue()

    @staticmethod
    def family_result(row: Row) -> ImportModelResult:
        return next(result for result in row.imported_models_results if result.model == Family)
