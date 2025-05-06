from django.db.models.query import QuerySet


class CampsReceiptQuerySet(QuerySet):

    def of_remittance(self, remittance):
        return self.filter(remittance=remittance)

    def of_family(self, family):
        return self.filter(camps_registration__child__family=family)

    def of_parent(self, parent):
        return self.filter(camps_registration__child__family__parents=parent)
