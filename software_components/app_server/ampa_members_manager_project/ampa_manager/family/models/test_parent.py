import phonenumbers
from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from .parent import Parent


class TestParent(TestCase):
    def test_str(self):
        parent: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        self.assertEqual(str(parent), str(parent.name_and_surnames) + " (" + str(parent.id) + ")")

    def test_create_no_unique_name_surname_family(self):
        parent: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        with self.assertRaises(IntegrityError):
            Parent.objects.create(name_and_surnames=parent.name_and_surnames)

    def test_create_unique_name_surname_family(self):
        baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        Parent.objects.create(name_and_surnames="name_and_surnames")
