from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.family.models.family import Family


class Child(models.Model):
    name = models.CharField(max_length=500)
    year_of_birth = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(3000)])
    repetition = models.IntegerField(default=0)
    family = models.ForeignKey(to=Family, on_delete=CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'family'], name='unique_child_name_in_a_family'),]

    @property
    def full_name(self) -> str:
        return f'{self.name} {str(self.family)}'

    def __str__(self) -> str:
        return self.full_name
