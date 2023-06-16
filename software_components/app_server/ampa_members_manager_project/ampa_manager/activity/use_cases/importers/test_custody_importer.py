from django.test import TestCase

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent


class TestCustodyImporter(TestCase):
    def test_count_objects(self):
        objects_counted: dict = CustodyImporter.count_objects()
        self.assertEqual(type(objects_counted), dict)
        self.assertEqual(objects_counted[Family.__name__], 0)
        self.assertEqual(objects_counted[Parent.__name__], 0)
        self.assertEqual(objects_counted[Child.__name__], 0)
        self.assertEqual(objects_counted[BankAccount.__name__], 0)
        self.assertEqual(objects_counted[Holder.__name__], 0)
        self.assertEqual(objects_counted[CustodyRegistration.__name__], 0)
        self.assertEqual(objects_counted[CustodyEdition.__name__], 0)
