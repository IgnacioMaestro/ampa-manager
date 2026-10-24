from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition


class AfterSchoolEditionConflict:
    def __init__(self, edition: AfterSchoolEdition, other: AfterSchoolEdition):
        self.edition = edition
        self.other = other


class AfterSchoolEditionConflictFinder:
    def find(
            self, kept: AfterSchool, editions_to_move: list[AfterSchoolEdition]) -> list[AfterSchoolEditionConflict]:
        conflicts = []
        indexed = {
            self._key(edition): edition
            for edition in kept.afterschooledition_set.all()
        }
        for edition in editions_to_move:
            key = self._key(edition)
            other = indexed.get(key)
            if other is not None:
                conflicts.append(AfterSchoolEditionConflict(edition, other))
            else:
                indexed[key] = edition
        return conflicts

    @staticmethod
    def _key(edition: AfterSchoolEdition) -> tuple:
        return edition.academic_course_id, edition.period, edition.timetable
