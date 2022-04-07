from django.db import models

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration


class IndividualActivityRegistrationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(registered_child__isnull=False)


class IndividualActivityRegistration(ActivityRegistration):
    objects = IndividualActivityRegistrationManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registered_family = None
        assert (self.registered_child is not None)

    class Meta:
        proxy = True
