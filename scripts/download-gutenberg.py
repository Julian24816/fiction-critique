from dataclasses import dataclass, asdict
from pathlib import Path
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from typing import List
import requests
import yaml

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


def download_rdf(book_id: int, directory: Path) -> Path:
    path = directory / f"{book_id}.rdf"
    r = requests.get(f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.rdf")
    r.raise_for_status()
    with path.open("wb") as f:
        f.write(r.content)
    return path

def download_text(book_id: int, directory: Path) -> Path:
    path = directory / f"{book_id}.txt"
    r = requests.get(f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt.utf8")
    r.raise_for_status()
    with path.open("wb") as f:
        f.write(r.content)
    return path


def parse_rdf(path: Path) -> GutenbergBook:
    g = Graph()
    g.parse(path)

    PGTERMS = Namespace("http://www.gutenberg.org/2009/pgterms/")
    DCTERMS = Namespace("http://purl.org/dc/terms/")

    def get_text(subject, predicate) -> str:
        return str(g.value(subject, predicate))

    def get_resource(subject, predicate) -> str:
        resource = g.value(subject, predicate)
        return resource.toPython() if resource else None

    ebook = URIRef("http://www.gutenberg.org/ebooks/100")

    publisher = get_text(ebook, DCTERMS.publisher)
    license = get_resource(ebook, DCTERMS.license)
    issued = get_text(ebook, DCTERMS.issued)
    rights = get_text(ebook, DCTERMS.rights)
    downloads = int(get_text(ebook, PGTERMS.downloads))

    creator_node = g.value(ebook, DCTERMS.creator)
    creator = Agent(
        name=get_text(creator_node, PGTERMS.name),
        birthdate=int(get_text(creator_node, PGTERMS.birthdate)),
        deathdate=int(get_text(creator_node, PGTERMS.deathdate)),
        aliases=[alias.toPython() for alias in g.objects(creator_node, PGTERMS.alias)],
        webpage=get_resource(creator_node, PGTERMS.webpage)
    )

    title = get_text(ebook, DCTERMS.title)
    description = get_text(ebook, PGTERMS.marc520)
    language = get_text(
        g.value(ebook, DCTERMS.language), RDF.value
    )
    subjects = [
        get_text(subject, RDF.value)
        for subject in g.objects(ebook, DCTERMS.subject)
    ]
    types = [
        get_text(type, RDF.value)
        for type in g.objects(ebook, DCTERMS.type)
    ]
    bookshelves = [
        get_text(shelf, RDF.value)
        for shelf in g.objects(ebook, PGTERMS.bookshelf)
    ]
    hasFormats = []
    for file_format in g.objects(ebook, DCTERMS.hasFormat):
        extents = [int(e) for e in g.objects(file_format, DCTERMS.extent)]
        modified = [str(m) for m in g.objects(file_format, DCTERMS.modified)]

        formats = []
        for format_ in g.objects(file_format, DCTERMS["format"]):
            format_value = get_text(format_, RDF.value)
            if format_value:
                formats.append(format_value)

        hasFormat = FileFormat(
            about=str(file_format),
            extents=extents,
            modified=modified,
            formats=formats
        )
        hasFormats.append(hasFormat)


    return GutenbergBook(
        publisher=publisher,
        license=license,
        issued=issued,
        rights=rights,
        downloads=downloads,
        creator=creator,
        title=title,
        description=description,
        language=language,
        subjects=subjects,
        types=types,
        bookshelves=bookshelves,
        hasFormats=hasFormats
    )

def save_as_yaml(book: GutenbergBook, directory: Path, book_id: int) -> Path:
    yaml_filepath = directory / f'{book_id}.yaml'
    with open(yaml_filepath, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(asdict(book), yaml_file, default_flow_style=False, allow_unicode=True)
    return yaml_filepath

if __name__ == "__main__":
    gut_dir = Path("data/gutenberg")
    gut_dir.mkdir(parents=True, exist_ok=True)
    rdf_path = download_rdf(100, gut_dir)
    text_path = download_text(100, gut_dir)
    the_book = parse_rdf(rdf_path)
    save_as_yaml(the_book, gut_dir, 100)
