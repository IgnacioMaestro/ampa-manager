from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Manager

if TYPE_CHECKING:
    from .authorization import Authorization


class AuthorizationManager(Manager):
    def next_order_for_year(self, year: int) -> int:
        authorization: Authorization = self.authorization_with_highest_order(year=year)
        if not authorization:
            return 1
        return authorization.order + 1
