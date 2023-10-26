from django.db.models.query import QuerySet


class CustodyReceiptQuerySet(QuerySet):

    def of_family(self, family):
        return self.filter(custody_registration__child__family=family)
