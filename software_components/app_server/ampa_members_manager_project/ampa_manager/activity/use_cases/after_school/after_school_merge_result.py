from django.utils.translation import gettext as _

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.use_cases.after_school.after_school_edition_conflict_finder import AfterSchoolEditionConflict


class AfterSchoolMergeResult:
    def __init__(self, succeeded: bool, lines: list[str]):
        self.succeeded = succeeded
        self.lines = lines

    @property
    def message(self) -> str:
        return '\n'.join(self.lines)

    @classmethod
    def success(
            cls, kept: AfterSchool, moved_editions: list[AfterSchoolEdition],
            deleted_activities: list[AfterSchool]) -> 'AfterSchoolMergeResult':
        lines = [
            _('After-school kept') + f': {kept.name} ({kept.id})',
            cls._editions_moved_line(moved_editions),
        ]
        for activity in deleted_activities:
            lines.append(_('After-school deleted') + f': {activity.name} ({activity.id})')
        return cls(True, lines)

    @classmethod
    def not_enough_activities(cls) -> 'AfterSchoolMergeResult':
        return cls(False, [_('No merge done. You have to select more than one after-school')])

    @classmethod
    def conflict(cls, conflicts: list[AfterSchoolEditionConflict]) -> 'AfterSchoolMergeResult':
        lines = [_('No merge done. These editions share the same course, period and timetable')]
        for found in conflicts:
            lines.append(
                f'{found.edition.str_short()} ({found.edition.id}) / '
                f'{found.other.str_short()} ({found.other.id})')
        return cls(False, lines)

    @classmethod
    def failed(cls, error: Exception) -> 'AfterSchoolMergeResult':
        return cls(False, [_('No merge done. Error') + f': {error}'])

    @staticmethod
    def _editions_moved_line(moved_editions: list[AfterSchoolEdition]) -> str:
        edition_ids = ', '.join(str(edition.id) for edition in moved_editions)
        if edition_ids:
            return _('Editions moved') + f': {len(moved_editions)} ({edition_ids})'
        return _('Editions moved') + ': 0'
