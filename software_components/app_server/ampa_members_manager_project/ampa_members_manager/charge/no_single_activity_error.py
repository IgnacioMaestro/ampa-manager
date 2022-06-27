from __future__ import annotations


class NoSingleActivityError(Exception):
    def __init__(self):
        super().__init__("NoSingleActivityError")
