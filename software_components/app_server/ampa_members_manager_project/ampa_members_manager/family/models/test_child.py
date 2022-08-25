from django.core.exceptions import ValidationError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.child import Child
from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.course_name import CourseName


class TestChild(TestCase):
    def test_str(self):
        child: Child = baker.make('Child')
        self.assertEqual(str(child), "{} {}".format(child.name, str(child.family)))

    def test_year_lower_minimal(self):
        with self.assertRaises(ValidationError):
            child: Child = Child(name='name_min', year_of_birth=999, family=baker.make('Family'))
            child.full_clean()

    def test_year_major_maximum(self):
        with self.assertRaises(ValidationError):
            child: Child = Child(name='name_min', year_of_birth=3001, family=baker.make('Family'))
            child.full_clean()

    def test_year_on_range(self):
        child: Child = Child(name='name_min', year_of_birth=2022, family=baker.make('Family'))
        child.full_clean()

    def test_get_course_name_hh2(self):
        academic_course: AcademicCourse = baker.make('AcademicCourse', initial_year=2022)
        ActiveCourse.objects.create(course=academic_course)

        child: Child = Child(name='name_min', year_of_birth=2020, family=baker.make('Family'))
        course_name = child.get_course_name()
        self.assertEqual(course_name, CourseName.HH2)

    def test_get_course_name_lh6(self):
        academic_course: AcademicCourse = baker.make('AcademicCourse', initial_year=2022)
        ActiveCourse.objects.create(course=academic_course)

        child: Child = Child(name='name_min', year_of_birth=2011, family=baker.make('Family'))
        course_name = child.get_course_name()
        self.assertEqual(course_name, CourseName.LH6)

    def test_get_course_name_hh2_one_repetition(self):
        academic_course: AcademicCourse = baker.make('AcademicCourse', initial_year=2022)
        ActiveCourse.objects.create(course=academic_course)

        child: Child = Child(name='name_min', year_of_birth=2019, repetition=1, family=baker.make('Family'))
        course_name = child.get_course_name()
        self.assertEqual(course_name, CourseName.HH2)

    def test_get_course_name_lh6_one_repetition(self):
        academic_course: AcademicCourse = baker.make('AcademicCourse', initial_year=2022)
        ActiveCourse.objects.create(course=academic_course)

        child: Child = Child(name='name_min', year_of_birth=2010, repetition=1, family=baker.make('Family'))
        course_name = child.get_course_name()
        self.assertEqual(course_name, CourseName.LH6)
    
    def test_get_course_name_out_due_to_one_year(self):
        academic_course: AcademicCourse = baker.make('AcademicCourse', initial_year=2022)
        ActiveCourse.objects.create(course=academic_course)

        child: Child = Child(name='name_min', year_of_birth=2021, family=baker.make('Family'))
        course_name = child.get_course_name()
        self.assertIsNone(course_name)
    
    def test_get_course_name_out_due_to_twelve_years(self):
        academic_course: AcademicCourse = baker.make('AcademicCourse', initial_year=2022)
        ActiveCourse.objects.create(course=academic_course)

        child: Child = Child(name='name_min', year_of_birth=2010, family=baker.make('Family'))
        course_name = child.get_course_name()
        self.assertIsNone(course_name)
