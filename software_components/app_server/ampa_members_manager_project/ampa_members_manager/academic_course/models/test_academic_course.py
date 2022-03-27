from unittest import TestCase

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse


class TestAcademicCourse(TestCase):
    def test_str(self):
        academic_course = AcademicCourse(initialYear=2022)
        self.assertEqual(str(academic_course), "2022-2023")
