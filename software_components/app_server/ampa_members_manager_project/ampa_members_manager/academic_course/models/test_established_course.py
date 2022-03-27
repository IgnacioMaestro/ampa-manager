from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.established_course import EstablishedCourse


class TestEstablishedCourse(TestCase):

    def test_str(self):
        academic_course = baker.make('AcademicCourse')
        established_course = EstablishedCourse.objects.create(course=academic_course, pk=2)
        self.assertEqual(str(established_course), 'SingletonEstablishedCourse')

    def test_save_always_pk_1(self):
        academic_course = baker.make('AcademicCourse')
        established_course = EstablishedCourse.objects.create(course=academic_course, pk=2)
        self.assertEqual(established_course.pk, 1)

    def test_delete_no_delete(self):
        academic_course = baker.make('AcademicCourse')
        established_course = EstablishedCourse.objects.create(course=academic_course, pk=2)
        established_course.delete()
        self.assertEqual(established_course.pk, 1)

    def test_load_no_established_course(self):
        with self.assertRaises(EstablishedCourse.DoesNotExist):
            EstablishedCourse.load()

    def test_load_established_course(self):
        academic_course = baker.make('AcademicCourse')
        EstablishedCourse.objects.create(course=academic_course, pk=2)
        loaded_academic_course = EstablishedCourse.load()
        self.assertEqual(academic_course, loaded_academic_course)
