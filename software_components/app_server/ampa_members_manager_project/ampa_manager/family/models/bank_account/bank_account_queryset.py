from django.db.models import Count, Q
from django.db.models.query import QuerySet


class BankAccountQuerySet(QuerySet):

    def of_family(self, family):
        return self.filter(owner__family=family)

    def with_swift_bic(self):
        return self.exclude(Q(swift_bic=None) | Q(swift_bic=""))

    def without_swift_bic(self):
        return self.filter(Q(swift_bic=None) | Q(swift_bic=""))

    def with_iban(self, iban):
        return self.filter(iban=iban)
