from django.db.models.query import QuerySet


class AfterSchoolReceiptQuerySet(QuerySet):

    def of_remittance(self, remittance):
        return self.filter(remittance=remittance)

    def of_family(self, family):
        return self.filter(after_school_registration__child__family=family)
