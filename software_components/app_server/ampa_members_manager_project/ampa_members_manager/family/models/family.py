from django.db import models


class Family(models.Model):
    first_surname = models.CharField(max_length=500)
    second_surname = models.CharField(max_length=500)
    email = models.EmailField(unique=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['first_surname', 'second_surname'], name='unique_surnames')]

    def __str__(self) -> str:
        return "{} {}".format(self.first_surname, self.second_surname)
