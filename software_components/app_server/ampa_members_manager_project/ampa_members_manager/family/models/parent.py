from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Parent(models.Model):
    name = models.CharField(max_length=500)
    first_surname = models.CharField(max_length=500)
    second_surname = models.CharField(max_length=500)
    phone_number = PhoneNumberField()
    additional_phone_number = PhoneNumberField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'first_surname', 'second_surname'], name='unique_parent')]

    @property
    def full_name(self) -> str:
        return f'{self.name} {self.first_surname} {self.second_surname}'

    def __str__(self) -> str:
        return self.full_name
