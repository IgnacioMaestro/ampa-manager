from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.family.models.family import Family


class Child(models.Model):
    name = models.CharField(max_length=500)
    year_of_birth = models.IntegerField()
    repetition = models.IntegerField(default=0)
    family = models.ForeignKey(to=Family, on_delete=CASCADE)

    def __str__(self) -> str:
        return "{} {}".format(self.name, str(self.family))
