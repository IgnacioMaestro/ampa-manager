from __future__ import annotations

from typing import Optional

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family


class CustodyImportationActionChild(models.Model):
    child_to_use = models.ForeignKey(
        'Child', on_delete=models.CASCADE, null=True, verbose_name=_("Use Child"), related_name='child_to_use')
    update_child_data = models.JSONField(default=dict, null=True, verbose_name=_("Update Child"))
    child_to_update = models.ForeignKey(
        'Child', on_delete=models.CASCADE, null=True, verbose_name=_("Child to update"), related_name='child_to_update')
    create_child_data = models.JSONField(default=dict, null=True, verbose_name=_("Create Child"))
    family_to_create_child = models.ForeignKey(
        'Family', on_delete=models.CASCADE, null=True, verbose_name=_("Family to create child"))

    class Meta:
        verbose_name = _("Custody importation action child")
        verbose_name_plural = _("Custody importation action children")
        constraints = [
            CheckConstraint(
                check=Q(child_to_use__isnull=False) | (
                        Q(update_child_data__isnull=False) & Q(child_to_update__isnull=False)) | (
                              Q(create_child_data__isnull=False) & Q(family_to_create_child__isnull=False)),
                name='child_constraint'
            )
        ]

    @classmethod
    def create_use_child(cls, child: Child) -> CustodyImportationActionChild:
        return CustodyImportationActionChild.objects.create(use_child=child)

    @classmethod
    def create_update_child(
            cls, child: Child, name: Optional[str] = None, year_of_birth: Optional[int] = None,
            repetition: Optional[int] = None) -> CustodyImportationActionChild:
        update_child_data = {}
        if name:
            update_child_data['name'] = name
        if year_of_birth:
            update_child_data['year_of_birth'] = year_of_birth
        if repetition:
            update_child_data['repetition'] = repetition
        return CustodyImportationActionChild.objects.create(update_child_data=update_child_data, child_to_update=child)

    @classmethod
    def create_create_child(cls, name: str, year_of_birth: int, repetition: Optional[int],
                            family: Family) -> CustodyImportationActionChild:
        create_child_data = {'name': name, 'year_of_birth': year_of_birth, 'family': family}
        if repetition:
            create_child_data.update({'repetition': repetition})
        return CustodyImportationActionChild.objects.create(
            create_child_data=create_child_data, family_to_create_child=family)
