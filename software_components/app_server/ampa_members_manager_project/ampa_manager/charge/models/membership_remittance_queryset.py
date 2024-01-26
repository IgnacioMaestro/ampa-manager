from django.db.models.query import QuerySet
from django.utils import timezone


class MembershipRemittanceQuerySet(QuerySet):

    def paid_on_current_year(self) -> QuerySet:
        return self.filter(payment_date__year=timezone.now().year)
