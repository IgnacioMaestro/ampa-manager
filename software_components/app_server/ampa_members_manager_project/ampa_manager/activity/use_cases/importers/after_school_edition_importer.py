from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult, ModifiedField


class AfterSchoolEditionImporter:

    def __init__(self, after_school: AfterSchool, academic_course: AcademicCourse, code: str, period: str,
                 timetable: str, levels: str, price_for_member: float, price_for_no_member: float):
        self.result = ImportModelResult(AfterSchoolEdition)
        self.after_school = after_school
        self.academic_course = academic_course
        self.code = code
        self.period = period
        self.timetable = timetable
        self.levels = levels
        self.price_for_member = price_for_member
        self.price_for_no_member = price_for_no_member
        self.edition = None

    def import_edition(self) -> ImportModelResult:
        try:
            error_message = self.validate_fields()

            if error_message is None:
                self.edition = self.find_after_school_edition()
                if self.edition:
                    self.manage_found_edition()
                else:
                    self.manage_not_found_edition()
            else:
                self.result.set_error(error_message)
        except Exception as e:
            self.result.set_error(str(e))

        return self.result

    def find_after_school_edition(self) -> Optional[AfterSchoolEdition]:
        try:
            return AfterSchoolEdition.objects.get(code=self.code)
        except AfterSchoolEdition.DoesNotExist:
            pass

        try:
            return AfterSchoolEdition.objects.get(
                after_school=self.after_school, academic_course=self.academic_course, period=self.period,
                timetable=self.timetable)
        except AfterSchoolEdition.DoesNotExist:
            return None

    def manage_not_found_edition(self):
        edition = AfterSchoolEdition.objects.create(
            after_school=self.after_school, academic_course=self.academic_course, code=self.code, period=self.period,
            timetable=self.timetable, price_for_member=self.price_for_member,
            price_for_no_member=self.price_for_no_member)
        self.result.set_created(edition)

    def manage_found_edition(self):
        if self.edition_is_modified():
            modified_fields = []

            if self.price_for_member is not None and self.price_for_member != self.edition.price_for_member:
                modified_fields.append(
                    ModifiedField(_('Price for members'), self.edition.price_for_member, self.price_for_member))
                self.edition.price_for_member = self.price_for_member

            if self.price_for_no_member is not None and self.price_for_no_member != self.edition.price_for_no_member:
                modified_fields.append(
                    ModifiedField(_('Price for non members'), self.edition.price_for_no_member, self.price_for_no_member))
                self.edition.price_for_no_member = self.price_for_no_member

            self.result.set_updated(self.edition, modified_fields)
        else:
            self.result.set_not_modified(self.edition)

    def validate_fields(self) -> Optional[str]:
        if not self.after_school:
            return _('Missing after school')

        if not self.academic_course:
            return _('Missing academic course')

        if not self.period:
            return _('Missing period')

        if not self.timetable:
            return _('Missing timetable')

        if not self.price_for_member or not isinstance(self.price_for_member, float):
            return _('Missing/Wrong price for members') + f' ({self.price_for_member})'

        if not self.price_for_no_member or not isinstance(self.price_for_no_member, float):
            return _('Missing/Wrong price for non members') + f' ({self.price_for_no_member})'

        return None

    def edition_is_modified(self):
        return (self.price_for_member != self.edition.price_for_member or
                self.price_for_no_member != self.edition.price_for_no_member)
