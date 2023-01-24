from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult


class AfterSchoolRegistrationImporter:

    @staticmethod
    def find(after_school_edition, child):
        try:
            return AfterSchoolRegistration.objects.get(after_school_edition=after_school_edition, child=child)
        except AfterSchoolRegistration.DoesNotExist:
            return None

    @staticmethod
    def import_registration(after_school_edition: AfterSchoolRegistration, holder: Holder, child: Child) -> ImportModelResult:
        result = ImportModelResult(AfterSchoolRegistration.__name__, [])

        registration = AfterSchoolRegistrationImporter.find(after_school_edition, child)
        if registration:
            if registration.holder != holder:
                fields_before = [registration.holder]
                registration.holder = holder
                fields_after = [registration.holder]
                registration.save()
                result.set_updated(registration, fields_before, fields_after)
            else:
                result.set_not_modified(registration)
        else:
            registration = AfterSchoolRegistration.objects.create(after_school_edition=after_school_edition,
                                                                  holder=holder, child=child)
            result.set_created(registration)

        return result
