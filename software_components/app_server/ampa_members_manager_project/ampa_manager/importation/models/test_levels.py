from __future__ import annotations

from django.test import TestCase

from ampa_manager.academic_course.models.level_constants import LevelConstants
from ampa_manager.importation.models.levels import Levels


class TestLevels(TestCase):
    def test_levels(self):
        self.assertEqual(
            Levels.choices,
            [(1, 'HH2'), (2, 'HH3'), (3, 'HH4'), (4, 'HH5'),
             (5, 'LH1'), (6, 'LH2'), (7, 'LH3'), (8, 'LH4'), (9, 'LH5'), (10, 'LH6')])
        self.assertEqual(Levels.values, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(Levels.labels, ['HH2', 'HH3', 'HH4', 'HH5', 'LH1', 'LH2', 'LH3', 'LH4', 'LH5', 'LH6'])
        self.assertEqual(Levels.names, ['HH2', 'HH3', 'HH4', 'HH5', 'LH1', 'LH2', 'LH3', 'LH4', 'LH5', 'LH6'])
        self.assertEqual(Levels.obtain_from_level_constant(LevelConstants.ID_HH3), 2)
