from __future__ import annotations


class NoActivityPayablePartError(Exception):
    def __init__(self):
        super().__init__("NoActivityPayablePartError")
