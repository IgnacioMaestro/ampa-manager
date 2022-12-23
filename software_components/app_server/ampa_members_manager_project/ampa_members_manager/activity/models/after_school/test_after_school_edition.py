from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition


class TestAfterSchoolEdition(TestCase):
    def test_meet_a_constraint(self):
        baker.make('AfterSchoolEdition')

        after_school_edition: AfterSchoolEdition = baker.make('AfterSchoolEdition')

        self.assertIsNotNone(after_school_edition)

    def test_no_meet_a_constraint(self):
        after_school_edition: AfterSchoolEdition = baker.make('AfterSchoolEdition')

        with self.assertRaises(IntegrityError):
            baker.make(
                'AfterSchoolEdition', after_school=after_school_edition.after_school,
                academic_course=after_school_edition.academic_course, period=after_school_edition.period,
                timetable=after_school_edition.timetable)

    def test_str(self):
        after_school_edition: AfterSchoolEdition = baker.make('AfterSchoolEdition')
        after_school_edition_str: str = f'{after_school_edition.after_school}'
        after_school_edition_str += f' {after_school_edition.period} {after_school_edition.timetable}'
        after_school_edition_str += f' {after_school_edition.academic_course}'
        self.assertEqual(str(after_school_edition), after_school_edition_str)
