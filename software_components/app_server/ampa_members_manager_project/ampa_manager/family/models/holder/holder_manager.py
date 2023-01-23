from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Manager

if TYPE_CHECKING:
    from .holder import Holder


class HolderManager(Manager):
    def next_order_for_year(self, year: int) -> int:
        holder: Holder = self.authorization_with_highest_order(year=year)
        if not holder:
            return 1
        return holder.authorization_order + 1
