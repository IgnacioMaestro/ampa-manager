from unittest.mock import patch

from django.test import TestCase
from django.utils.translation import gettext as _
from model_bakery import baker

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.use_cases.after_school.after_school_merger import AfterSchoolMerger
from ampa_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestAfterSchoolMerger(TestCase):
    def test_moves_editions_to_the_first_and_keeps_its_name(self):
        course = baker.make(AcademicCourse)
        kept = baker.make(AfterSchool, name='Alpha')
        with_edition = baker.make(AfterSchool, name='Beta')
        without_edition = baker.make(AfterSchool, name='Gamma')
        kept_edition = self._edition(kept, course, period='1', timetable='Lunes', code='K')
        moved_edition = self._edition(with_edition, course, period='2', timetable='Martes', code='B')
        registration = baker.make(AfterSchoolRegistration, after_school_edition=moved_edition)

        result = AfterSchoolMerger().merge(self._ordered_by_name(kept, with_edition, without_edition))

        self.assertTrue(result.succeeded)
        kept.refresh_from_db()
        moved_edition.refresh_from_db()
        kept_edition.refresh_from_db()
        self.assertEqual(kept.name, 'Alpha')
        self.assertEqual(moved_edition.after_school_id, kept.id)
        self.assertEqual(kept_edition.after_school_id, kept.id)
        self.assertTrue(AfterSchoolRegistration.objects.filter(id=registration.id).exists())
        self.assertFalse(AfterSchool.objects.filter(id__in=[with_edition.id, without_edition.id]).exists())
        self.assertIn(_('After-school kept') + ': Alpha', result.message)
        self.assertIn(str(moved_edition.id), result.message)
        self.assertIn('Beta', result.message)
        self.assertIn('Gamma', result.message)
        self.assertNotIn(' | ', kept.name)

    def test_keeps_the_first_of_the_queryset_order(self):
        kept = baker.make(AfterSchool, name='Zebra')
        removed = baker.make(AfterSchool, name='Alpha')
        activities = AfterSchool.objects.filter(id__in=[kept.id, removed.id]).order_by('-name')

        result = AfterSchoolMerger().merge(activities)

        self.assertTrue(result.succeeded)
        kept.refresh_from_db()
        self.assertEqual(kept.name, 'Zebra')
        self.assertFalse(AfterSchool.objects.filter(id=removed.id).exists())

    def test_does_nothing_when_only_one_activity_is_selected(self):
        activity = baker.make(AfterSchool, name='Alpha')

        result = AfterSchoolMerger().merge(AfterSchool.objects.filter(id=activity.id))

        self.assertFalse(result.succeeded)
        self.assertEqual(
            result.message, _('No merge done. You have to select more than one after-school'))
        self.assertTrue(AfterSchool.objects.filter(id=activity.id, name='Alpha').exists())

    def test_does_nothing_when_an_edition_conflicts_with_the_kept_activity(self):
        course = baker.make(AcademicCourse)
        kept = baker.make(AfterSchool, name='Alpha')
        source = baker.make(AfterSchool, name='Beta')
        kept_edition = self._edition(kept, course, period='1', timetable='Lunes', code='K')
        source_edition = self._edition(source, course, period='1', timetable='Lunes', code='B')

        result = AfterSchoolMerger().merge(self._ordered_by_name(kept, source))

        self.assertFalse(result.succeeded)
        self.assertIn(str(kept_edition.id), result.message)
        self.assertIn(str(source_edition.id), result.message)
        source_edition.refresh_from_db()
        self.assertEqual(source_edition.after_school_id, source.id)
        self.assertTrue(AfterSchool.objects.filter(id=source.id).exists())
        kept.refresh_from_db()
        self.assertEqual(kept.name, 'Alpha')

    def test_does_nothing_when_editions_from_different_activities_conflict(self):
        course = baker.make(AcademicCourse)
        kept = baker.make(AfterSchool, name='Alpha')
        first_source = baker.make(AfterSchool, name='Beta')
        second_source = baker.make(AfterSchool, name='Gamma')
        self._edition(kept, course, period='1', timetable='Lunes', code='K')
        first_edition = self._edition(first_source, course, period='2', timetable='Martes', code='B')
        second_edition = self._edition(second_source, course, period='2', timetable='Martes', code='G')

        result = AfterSchoolMerger().merge(self._ordered_by_name(kept, first_source, second_source))

        self.assertFalse(result.succeeded)
        self.assertIn(str(first_edition.id), result.message)
        self.assertIn(str(second_edition.id), result.message)
        first_edition.refresh_from_db()
        second_edition.refresh_from_db()
        self.assertEqual(first_edition.after_school_id, first_source.id)
        self.assertEqual(second_edition.after_school_id, second_source.id)
        self.assertTrue(AfterSchool.objects.filter(id__in=[first_source.id, second_source.id]).exists())

    def test_rolls_back_when_a_save_fails(self):
        course = baker.make(AcademicCourse)
        kept = baker.make(AfterSchool, name='Alpha')
        source = baker.make(AfterSchool, name='Beta')
        first_edition = self._edition(source, course, period='1', timetable='Lunes', code='B1')
        second_edition = self._edition(source, course, period='2', timetable='Martes', code='B2')
        original_save = AfterSchoolEdition.save

        def save_and_fail_on_second(edition, *args, **kwargs):
            save_and_fail_on_second.calls += 1
            if save_and_fail_on_second.calls > 1:
                raise RuntimeError('forced failure')
            return original_save(edition, *args, **kwargs)

        save_and_fail_on_second.calls = 0
        with patch.object(AfterSchoolEdition, 'save', save_and_fail_on_second):
            result = AfterSchoolMerger().merge(self._ordered_by_name(kept, source))

        self.assertFalse(result.succeeded)
        self.assertIn('forced failure', result.message)
        first_edition.refresh_from_db()
        second_edition.refresh_from_db()
        self.assertEqual(first_edition.after_school_id, source.id)
        self.assertEqual(second_edition.after_school_id, source.id)
        self.assertTrue(AfterSchool.objects.filter(id=source.id).exists())
        kept.refresh_from_db()
        self.assertEqual(kept.name, 'Alpha')

    def _edition(self, after_school, course, period, timetable, code) -> AfterSchoolEdition:
        return baker.make(
            AfterSchoolEdition, after_school=after_school, academic_course=course, period=period,
            timetable=timetable, code=code)

    def _ordered_by_name(self, *activities):
        return AfterSchool.objects.filter(id__in=[activity.id for activity in activities]).order_by('name')
