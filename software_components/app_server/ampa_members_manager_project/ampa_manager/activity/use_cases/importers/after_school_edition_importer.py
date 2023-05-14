from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.family.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult


class AfterSchoolEditionImporter:

    @staticmethod
    def find_edition_for_active_course(after_school, period, timetable, levels):
        academic_course = ActiveCourse.load()
        editions = AfterSchoolEdition.objects.filter(period=period, timetable=timetable, after_school=after_school,
                                                     levels=levels, academic_course=academic_course)
        if editions.count() == 1:
            return editions[0]
        return None

    @staticmethod
    def create_edition_for_active_course(after_school, period, timetable, levels, price_for_member, price_for_no_member):
        return AfterSchoolEdition.objects.create(after_school=after_school, period=period,
                                                 timetable=timetable, levels=levels,
                                                 academic_course=ActiveCourse.load(),
                                                 price_for_member=price_for_member,
                                                 price_for_no_member=price_for_no_member)

    @staticmethod
    def import_edition(after_school, code, period, timetable, levels, price_for_members, price_for_no_members) -> ImportModelResult:
        result = ImportModelResult(AfterSchoolEdition.__name__, [code, period, timetable, levels, price_for_members,
                                                                 price_for_no_members])

        edition = AfterSchoolEdition.find(code)
        if not edition:
            edition = AfterSchoolEditionImporter.find_edition_for_active_course(after_school, period, timetable, levels)

        if edition:
            if edition.is_modified(after_school, code, period, timetable, levels, price_for_members, price_for_no_members):
                fields_changes: FieldsChanges = edition.update(after_school, code, period, timetable, levels, price_for_members, price_for_no_members)
                result.set_updated(edition, fields_changes)
            else:
                result.set_not_modified(edition)
        else:
            edition = AfterSchoolEditionImporter.create_edition_for_active_course(after_school, period, timetable,
                                                                                  levels, price_for_members,
                                                                                  price_for_no_members)
            result.set_created(edition)

        return result

    @staticmethod
    def import_edition_by_code(code) -> ImportModelResult:
        result = ImportModelResult(AfterSchoolEdition.__name__, [code])

        edition = AfterSchoolEdition.find(code)
        if edition:
            result.set_not_modified(edition)
        else:
            result.set_not_found()

        return result
