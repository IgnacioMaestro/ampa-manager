from django.db.models.query import QuerySet


class CustodyEditionQuerySet(QuerySet):

    def with_remittance(self):
        return self.all()

    def without_remittance(self):
        return self.all()
