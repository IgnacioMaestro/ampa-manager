from django.db import models
from django.utils.translation import gettext_lazy as _


class NameableWithDate(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Name"),
                            help_text=_("Name to identify the remittance. Maximum 30 characters"))
    sepa_id = models.CharField(max_length=300, null=True, blank=True, verbose_name=_("Sepa_id"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    payment_date = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name=_("Payment date"))
    concept = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Concept"),
                               help_text=_("Description that the families will see in the bank account. Maximum 30 characters"))

    class Meta:
        abstract = True

    @property
    def name_with_date(self) -> str:
        time_name = '_' + self.created_at.strftime("%Y%m%d_%H%M%S")
        if self.name:
            return self.name + time_name
        return time_name

    def is_filled(self) -> bool:
        name_not_none = self.name is not None
        date_not_none = self.payment_date is not None
        concept_not_none = self.concept is not None
        sepa_id_not_none = self.sepa_id is not None
        return name_not_none and date_not_none and concept_not_none and sepa_id_not_none
