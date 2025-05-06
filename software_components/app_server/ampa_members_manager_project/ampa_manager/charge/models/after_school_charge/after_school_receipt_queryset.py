from django.db.models.query import QuerySet


class AfterSchoolReceiptQuerySet(QuerySet):

    def of_remittance(self, remittance):
        return self.filter(remittance=remittance)

    def of_family(self, family):
        return self.filter(after_school_registration__child__family=family)

    def of_parent(self, parent):
        return self.filter(after_school_registration__holder__parent=parent)

    def of_edition(self, edition):
        return self.filter(after_school_registration__after_school_edition=edition)
