from django.db import models

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration


class FamiliarActivityRegistrationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(registered_family__isnull=False)


class FamiliarActivityRegistration(ActivityRegistration):
    objects = FamiliarActivityRegistrationManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registered_child = None
        assert (self.registered_family is not None)

    class Meta:
        proxy = True
