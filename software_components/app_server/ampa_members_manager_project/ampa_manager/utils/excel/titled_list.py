from __future__ import  annotations
from typing import List


class TitledList:
    title: str
    elements: List[str]
    sublists: List[TitledList]

    def __init__(self, title):
        self.title = title
        self.elements = []
        self.sublists = []

    def __str__(self):
        return f'{self.title} ({len(self.elements)} elements, {len(self.sublists)} lists)'

    def append_element(self, element: str):
        self.elements.append(element)

    def append_sublist(self, sublist: TitledList):
        self.sublists.append(sublist)
