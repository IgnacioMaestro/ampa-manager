from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.use_cases.old_importers.excel.import_model_result import ImportModelResult
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.activity.use_cases.importers.fields_changes import FieldsChanges


class CampsRegistrationImporter:

    @staticmethod
    def find(camps_edition: CampsEdition, child: Child):
        try:
            return CampsRegistration.objects.get(camps_edition=camps_edition, child=child)
        except CampsRegistration.DoesNotExist:
            return None

    @staticmethod
    def import_registration(camps_edition: CampsEdition, holder: Holder, child: Child) -> ImportModelResult:
        result = ImportModelResult(CampsRegistration, [camps_edition, holder, child])

        registration = CampsRegistrationImporter.find(camps_edition, child)
        if registration:
            if registration.holder != holder:
                fields_before = [registration.holder]
                registration.holder = holder
                fields_after = [registration.holder]
                registration.save()
                result.set_updated(registration, FieldsChanges(fields_before, fields_after, []))
            else:
                result.set_not_modified(registration)
        else:
            registration = CampsRegistration.objects.create(camps_edition=camps_edition, holder=holder, child=child)
            result.set_created(registration)

        return result
