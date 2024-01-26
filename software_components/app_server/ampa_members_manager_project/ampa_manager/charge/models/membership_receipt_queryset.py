from django.db.models import Count, Q, Sum
from django.db.models.query import QuerySet


class MembershipReceiptQuerySet(QuerySet):

    def of_remittance(self, remittance):
        return self.filter(remittance=remittance)

    def of_family(self, family):
        return self.filter(family=family)
