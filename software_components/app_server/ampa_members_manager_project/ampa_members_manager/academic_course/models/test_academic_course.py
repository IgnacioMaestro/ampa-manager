from unittest import TestCase

from django.core.exceptions import ValidationError

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class TestAcademicCourse(TestCase):
    def test_str(self):
        academic_course = AcademicCourse(initialYear=2022)
        self.assertEqual(str(academic_course), "2022-2023")

    def test_year_lower_minimal(self):
        with self.assertRaises(ValidationError):
            child: AcademicCourse = AcademicCourse(initialYear=999)
            child.full_clean()

    def test_year_major_maximum(self):
        with self.assertRaises(ValidationError):
            child: AcademicCourse = AcademicCourse(initialYear=3001)
            child.full_clean()

    def test_year_on_range(self):
        child: AcademicCourse = AcademicCourse(initialYear=2022)
        child.full_clean()
