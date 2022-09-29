from django.db import models
from django.utils.translation import gettext_lazy as _


class State(models.IntegerChoices):
    NOT_SENT = (1, _('Not sent'))
    SENT = (2, _('Sent'))
    SIGNED = (3, _('Signed'))

    @staticmethod
    def get_value_hunman_name(value):
        if value == State.NOT_SENT:
            return State.NOT_SENT.label
        elif value == State.SENT:
            return State.SENT.label
        elif value == State.SIGNED:
            return State.SIGNED.label
