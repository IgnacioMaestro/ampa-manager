from django.db import models


class SingleActivity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f'{self.name}'
