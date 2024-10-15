from typing import List, Mapping
from collections import OrderedDict
from datetime import datetime

MD = str
FictionStats = Mapping[str, int|datetime]

class Fiction:
    """A work of fiction on royalroad.com"""
    def __init__(self, slot:int, title:str, tags:List[str], stats:FictionStats, description:MD):
        self.slot = slot
        self.title = title
        self.tags = tags
        self.stats = stats
        self.description = description

    def to_ordered_dict(self):
        return OrderedDict([
            ('slot', self.slot),
            ('title', self.title),
            ('tags', self.tags),
            ('stats', self.stats),
            ('description', self.description)
        ])

    def __eq__(self, other):
        if not isinstance(other, Fiction):
            return False
        return (self.slot == other.slot and
                self.title == other.title and
                self.tags == other.tags and
                self.stats == other.stats and
                self.description == other.description)


