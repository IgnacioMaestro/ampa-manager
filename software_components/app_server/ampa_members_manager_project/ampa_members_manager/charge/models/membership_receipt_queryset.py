from django.db.models import Count, Q, Sum
from django.db.models.query import QuerySet


class MembershipReceiptQuerySet(QuerySet):

    def of_remittance(self, remittance):
        return self.filter(remittance=remittance)
    
    def get_total(self):
        result = self.aggregate(total=Sum('total'))
        return result.get('total')
