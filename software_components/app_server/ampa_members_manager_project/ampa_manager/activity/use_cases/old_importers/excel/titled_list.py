from __future__ import  annotations
from typing import List

from ampa_manager.utils.string_utils import StringUtils


class TitledList:
    id: str
    title: str
    elements: List[str]
    sublists: List[TitledList]

    def __init__(self, title, sublists=None, elements=None):
        self.id = StringUtils.normalize(StringUtils.remove_all_spaces(title))
        self.title = title
        self.elements = elements if elements is not None else []
        self.sublists = sublists if sublists is not None else []

    def __str__(self):
        return f'{self.title} ({len(self.elements)} elements, {len(self.sublists)} lists)'

    def append_element(self, element: str):
        self.elements.append(element)

    def append_sublist(self, sublist: TitledList):
        self.sublists.append(sublist)
