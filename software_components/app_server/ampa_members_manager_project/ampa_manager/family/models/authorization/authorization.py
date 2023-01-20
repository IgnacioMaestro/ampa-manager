import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .authorization_manager import AuthorizationManager
from .authorization_queryset import AuthorizationQueryset
from ..state import State


class Authorization(models.Model):
    order = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999)], verbose_name=_("Order"))
    year = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Year"))
    sign_date = models.DateField(default=datetime.date.today)
    document = models.FileField(null=True, blank=True, upload_to='authorizations/', verbose_name=_("Document"))
    state = models.IntegerField(choices=State.choices, default=State.NOT_SENT, verbose_name=_("State"))

    objects = AuthorizationManager.from_queryset(AuthorizationQueryset)()

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=['order', 'year'], name='%(class)s_unique_order_in_a_year')]

    def clean(self):
        if self.state == State.SIGNED and not self.document:
            raise ValidationError(_('The state can not be sent or signed if there is no document attached'))

    @property
    def full_number(self) -> str:
        return f'{self.year}/{self.order:03}'
