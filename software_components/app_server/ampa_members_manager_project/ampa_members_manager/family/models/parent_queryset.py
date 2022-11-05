from django.db.models.query import QuerySet
from django.db.models import Count, Q


class ParentQuerySet(QuerySet):

    def by_full_name(self, full_name):
        return self.filter(name_and_surnames__iexact=full_name)

    def has_no_family(self):
        self = self.annotate(family_count=Count('family'))
        return self.filter(family_count=0)
    
    def has_one_family(self):
        self = self.annotate(family_count=Count('family'))
        return self.filter(family_count=1)

    def has_multiple_families(self):
        self = self.annotate(family_count=Count('family'))
        return self.filter(family_count__gt=1)
    
    def with_email(self):
        return self.exclude(Q(email=None) | Q(email=''))
    
    def without_email(self):
        return self.filter(Q(email=None) | Q(email=''))