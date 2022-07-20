from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.active_course import ActiveCourse


class TestActiveCourse(TestCase):

    def test_str(self):
        academic_course = baker.make('AcademicCourse')
        established_course = ActiveCourse.objects.create(course=academic_course, pk=2)
        self.assertEqual(str(established_course), str(academic_course))

    def test_save_always_pk_1(self):
        academic_course = baker.make('AcademicCourse')
        established_course = ActiveCourse.objects.create(course=academic_course, pk=2)
        self.assertEqual(established_course.pk, 1)

    def test_delete_no_delete(self):
        academic_course = baker.make('AcademicCourse')
        established_course = ActiveCourse.objects.create(course=academic_course, pk=2)
        established_course.delete()
        self.assertEqual(established_course.pk, 1)

    def test_load_no_established_course(self):
        with self.assertRaises(ActiveCourse.DoesNotExist):
            ActiveCourse.load()

    def test_load_established_course(self):
        academic_course = baker.make('AcademicCourse')
        ActiveCourse.objects.create(course=academic_course, pk=2)
        loaded_academic_course = ActiveCourse.load()
        self.assertEqual(academic_course, loaded_academic_course)
