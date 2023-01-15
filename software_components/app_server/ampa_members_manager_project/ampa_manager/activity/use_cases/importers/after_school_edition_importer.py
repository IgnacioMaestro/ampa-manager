from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
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
    def import_edition(after_school, period, timetable, levels, price_for_members, price_for_no_members,
                       create_if_not_exists) -> ImportModelResult:
        result = ImportModelResult(AfterSchoolEdition.__name__, [period, timetable, levels, price_for_members, price_for_no_members])

        edition = AfterSchoolEditionImporter.find_edition_for_active_course(after_school, period, timetable, levels)
        if edition:
            result.set_not_modified(edition)
        elif create_if_not_exists:
            edition = AfterSchoolEditionImporter.create_edition_for_active_course(after_school, period, timetable, levels,
                                                        price_for_members, price_for_no_members)
            result.set_created(edition)
        else:
            result.set_error(f'Not found: {after_school}, {period}, {timetable}, {levels}')

        return result
