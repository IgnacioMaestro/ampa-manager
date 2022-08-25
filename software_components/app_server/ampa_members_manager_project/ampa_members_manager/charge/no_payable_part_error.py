from __future__ import annotations


class NoActivityPeriodError(Exception):
    def __init__(self):
        super().__init__("NoActivityPeriodError")
