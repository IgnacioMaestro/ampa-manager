from django.db.models.query import QuerySet

from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.family.models.child import Child


class AfterSchoolRegistrationQuerySet(QuerySet):

    def of_after_school_remittance(self, after_school_remittance: AfterSchoolRemittance):
        return self.filter(after_school_edition__after_school_remittance=after_school_remittance)

    def of_child(self, child: Child):
        return self.filter(child=child)
