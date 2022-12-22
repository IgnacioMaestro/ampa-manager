from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_members_manager.baker_recipes import bank_account_recipe
from ampa_members_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_members_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_members_manager.charge.no_after_school_edition_error import NoAfterSchoolEditionError
from ampa_members_manager.charge.use_cases.create_after_school_remittance_with_receipts.after_school_remittance_with_receipts_creator import \
    AfterSchoolRemittanceWithReceiptsCreator


class TestAfterSchoolRemittanceWithReceiptsCreator(TestCase):
    def test_create_no_after_school_edition(self):
        with self.assertRaises(NoAfterSchoolEditionError):
            AfterSchoolRemittanceWithReceiptsCreator(AfterSchoolEdition.objects.none()).create()

    def test_create_after_school_edition_with_after_school_registration(self):
        baker.make('AfterSchoolRegistration', bank_account=baker.make_recipe(bank_account_recipe))

        after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittanceWithReceiptsCreator(
            AfterSchoolEdition.objects.all()).create()

        self.assertIsNotNone(after_school_remittance)
        AfterSchoolReceipt.objects.get(remittance=after_school_remittance)
