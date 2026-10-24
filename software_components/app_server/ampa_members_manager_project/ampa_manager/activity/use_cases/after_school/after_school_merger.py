from django.db import transaction
from django.db.models import QuerySet

from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.use_cases.after_school.after_school_edition_conflict_finder import \
    AfterSchoolEditionConflictFinder
from ampa_manager.activity.use_cases.after_school.after_school_edition_mover import AfterSchoolEditionMover
from ampa_manager.activity.use_cases.after_school.after_school_merge_result import AfterSchoolMergeResult


class AfterSchoolMerger:
    def merge(self, after_schools: QuerySet[AfterSchool]) -> AfterSchoolMergeResult:
        if after_schools.count() < 2:
            return AfterSchoolMergeResult.not_enough_activities()

        kept = after_schools.first()
        sources = list(after_schools.exclude(pk=kept.pk))
        editions_to_move = list(
            AfterSchoolEdition.objects.filter(after_school__in=sources).order_by('id'))
        conflicts = AfterSchoolEditionConflictFinder().find(kept, editions_to_move)
        if conflicts:
            return AfterSchoolMergeResult.conflict(conflicts)

        try:
            with transaction.atomic():
                AfterSchoolEditionMover().move(editions_to_move, kept)
                for source in sources:
                    source.delete()
        except Exception as error:
            return AfterSchoolMergeResult.failed(error)

        return AfterSchoolMergeResult.success(kept, editions_to_move, sources)
