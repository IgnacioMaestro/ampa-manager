from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult


class CustodyRegistrationImporter:

    @staticmethod
    def find(custody_edition, child):
        try:
            return CustodyRegistration.objects.get(custody_edition=custody_edition, child=child)
        except CustodyRegistration.DoesNotExist:
            return None

    @staticmethod
    def import_registration(custody_edition: CustodyRegistration, holder: Holder, child: Child, assisted_days: int) -> ImportModelResult:
        result = ImportModelResult(CustodyRegistration.__name__, [])

        registration = CustodyRegistrationImporter.find(custody_edition, child)
        if registration:
            if registration.holder != holder or registration.assisted_days != assisted_days:
                fields_before = [registration.holder, registration.assisted_days]
                registration.holder = holder
                registration.assisted_days = assisted_days
                fields_after = [registration.holder, registration.assisted_days]
                registration.save()
                result.set_updated(registration, FieldsChanges(fields_before, fields_after, []))
            else:
                result.set_not_modified(registration)
        else:
            registration = CustodyRegistrationImporter.objects.create(custody_edition=custody_edition, holder=holder,
                                                                      child=child, assisted_days=assisted_days)
            result.set_created(registration)

        return result