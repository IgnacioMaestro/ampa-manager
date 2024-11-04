from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.camps.camps_edition import CampsEdition


class TestCampsEdition(TestCase):
    def test_meet_unique_academic_course_with_levels_constraint(self):
        baker.make(CampsEdition)

        camps_edition: CampsEdition = baker.make(CampsEdition)

        self.assertIsNotNone(camps_edition)

    def test_no_meet_unique_academic_course_with_levels_constraint(self):
        camps_edition: CampsEdition = baker.make(CampsEdition)

        with self.assertRaises(IntegrityError):
            baker.make(CampsEdition, academic_course=camps_edition.academic_course, levels=camps_edition.levels)
