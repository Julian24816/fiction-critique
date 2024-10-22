from typing import List, Mapping
from collections import OrderedDict
from datetime import datetime

MD = str
FictionStats = Mapping[str, int|datetime]

class Fiction:
    """A work of fiction on royalroad.com"""
    def __init__(self, slot:int, title:str, author:str, description:MD,
                 tags:List[str], stats:FictionStats, chapters:List[int]):
        self.slot = slot
        self.title = title
        self.author = author
        self.description = description
        self.tags = tags
        self.stats = stats
        self.chapters = chapters

    def to_ordered_dict(self):
        return OrderedDict([
            ('slot', self.slot),
            ('title', self.title),
            ('author', self.author),
            ('tags', self.tags),
            ('stats', self.stats),
            ('chapters', self.chapters),
            ('description', self.description)
        ])

    def __eq__(self, other):
        if not isinstance(other, Fiction):
            return False
        return (self.slot == other.slot and
                self.title == other.title and
                self.author == other.author and
                self.tags == other.tags and
                self.stats == other.stats and
                self.description == other.description)

    def __repr__(self):
        return (f"Fiction(slot={self.slot!r}, title={self.title!r}, author={self.author!r}, "
                f"tags={self.tags!r}, stats={self.stats!r}, chapters={self.chapters!r}, "
                "description={self.description!r})")

    def __str__(self):
        return (f"Fiction: {self.title}\n"
                f"Slot: {self.slot}\n"
                f"Author: {self.author}\n"
                f"Tags: {', '.join(self.tags)}\n"
                f"Stats:\n    {'\n    '.join(f"{key}: {value}" for key,value in self.stats.items())}\n"
                f"Chapters: ({len(self.chapters)}) {', '.join(str(i) for i in self.chapters)}\n"
                f"Description:\n{self.description}")

