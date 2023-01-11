from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.management.commands.results.model_import_result import ModelImportResult


class AfterSchoolRegistrationImporter:

    @staticmethod
    def find(after_school_edition, child):
        try:
            return AfterSchoolRegistration.objects.get(after_school_edition=after_school_edition, child=child)
        except AfterSchoolRegistration.DoesNotExist:
            return None

    @staticmethod
    def import_registration(after_school_edition, bank_account, child) -> ModelImportResult:
        result = ModelImportResult(AfterSchoolRegistration.__name__)

        registration = AfterSchoolRegistrationImporter.find(after_school_edition, child)
        if registration:
            if registration.bank_account != bank_account:
                fields_before = [registration.bank_account]
                registration.bank_account = bank_account
                fields_after = [registration.bank_account]
                registration.save()
                result.set_updated(registration, fields_before, fields_after)
            else:
                result.set_not_modified(registration)
        else:
            registration = AfterSchoolRegistration.objects.create(after_school_edition=after_school_edition,
                                                                  bank_account=bank_account, child=child)
            result.set_created(registration)

        return result
