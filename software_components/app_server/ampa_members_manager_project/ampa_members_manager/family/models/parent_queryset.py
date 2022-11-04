from django.db.models.query import QuerySet


class ParentQuerySet(QuerySet):

    def by_full_name(self, full_name):
        return self.filter(name_and_surnames__iexact=full_name)
