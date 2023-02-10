from django.db import models
from django.utils.translation import gettext_lazy as _


class NameableWithDate(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True, verbose_name=_("Name"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        abstract = True

    @property
    def name_with_date(self) -> str:
        time_name = '_' + self.created_at.strftime("%Y%m%d_%H%M%S")
        if self.name:
            return self.name + time_name
        return time_name
