from django.db.models.query import QuerySet


class CampsEditionQuerySet(QuerySet):

    def with_remittance(self):
        return self.all()

    def without_remittance(self):
        return self.all()
