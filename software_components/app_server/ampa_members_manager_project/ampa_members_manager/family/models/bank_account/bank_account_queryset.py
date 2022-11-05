from django.db.models import Count, Q
from django.db.models.query import QuerySet


class BankAccountQuerySet(QuerySet):

    def of_family(self, family):
        return self.filter(owner__family=family)

    def with_authorization_state(self, state):
        return self.filter(authorization__state=state)

    def without_authorization(self):
        self = self.annotate(auth_count=Count('authorization'))
        return self.filter(auth_count=0)

    def with_swift_bic(self):
        return self.exclude(Q(swift_bic=None) | Q(swift_bic=""))

    def without_swift_bic(self):
        return self.filter(Q(swift_bic=None) | Q(swift_bic=""))

    def with_iban(self, iban):
        return self.filter(iban=iban)