from django.db.models.query import QuerySet


class CampsReceiptQuerySet(QuerySet):

    def of_family(self, family):
        return self.filter(camps_registration__child__family=family)
