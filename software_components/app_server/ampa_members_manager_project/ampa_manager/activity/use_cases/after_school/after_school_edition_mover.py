from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition


class AfterSchoolEditionMover:
    def move(self, editions: list[AfterSchoolEdition], target: AfterSchool) -> None:
        for edition in editions:
            edition.after_school = target
            edition.save(update_fields=['after_school'])
