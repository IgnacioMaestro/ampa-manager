from django.db.models.query import QuerySet


class CustodyReceiptQuerySet(QuerySet):

    def of_remittance(self, remittance):
        return self.filter(remittance=remittance)

    def of_family(self, family):
        return self.filter(custody_registration__child__family=family)

    def of_parent(self, parent):
        return self.filter(custody_registration__child__family__parents=parent)
