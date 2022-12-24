from django.db.models.query import QuerySet


class ActivityReceiptQuerySet(QuerySet):

    def of_family(self, family):
        return self.filter(activity_registrations__child__family=family)
