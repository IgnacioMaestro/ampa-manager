from django.db import models


class Parent(models.Model):
    name = models.CharField(max_length=500)
    first_surname = models.CharField(max_length=500)
    second_surname = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=12)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'first_surname', 'second_surname'], name='unique_parent')]

    def __str__(self) -> str:
        return "{} {} {}".format(self.name, self.first_surname, self.second_surname)
