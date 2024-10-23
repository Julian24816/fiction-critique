from dataclasses import dataclass
from typing import List

@dataclass
class Agent:
    name: str
    birthdate: int
    deathdate: int
    aliases: List[str]
    webpage: str

@dataclass
class FileFormat:
    about: str
    extents: List[int]
    modified: List[str]
    formats: List[str]

@dataclass
class GutenbergBook:
    publisher: str
    license: str
    issued: str
    rights: str
    downloads: int
    creator: Agent
    title: str
    description: str
    language: str
    subjects: List[str]
    types: List[str]
    bookshelves: List[str]
    hasFormats: List[FileFormat]