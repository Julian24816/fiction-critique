from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
import requests

from fictique.model.gutenberg import GutenbergBook, Agent, FileFormat


def download_rdf(book_id: int, directory: Path) -> Path:
    path = directory / f"{book_id}.rdf"
    r = requests.get(f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.rdf")
    r.raise_for_status()
    with path.open("wb") as f:
        f.write(r.content)
    return path

def download_text(book_id: int, directory: Path, utf8version: bool = True) -> Path:
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    if utf8version:
        url += ".utf8"

    r = requests.get(url)
    r.raise_for_status()

    path = directory / f"{book_id}.txt"
    with path.open("wb") as f:
        f.write(r.content)
    return path

def parse_rdf(path: Path) -> GutenbergBook:
    g = Graph()
    g.parse(path)

    PGTERMS = Namespace("http://www.gutenberg.org/2009/pgterms/")
    DCTERMS = Namespace("http://purl.org/dc/terms/")

    def get_text(subject, predicate) -> str:
        value = g.value(subject, predicate)
        if value:
            return str(value)
        return ''

    def get_resource(subject, predicate) -> str:
        resource = g.value(subject, predicate)
        return resource.toPython() if resource else ''

    def try_get_int(value: str, else_result: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return else_result

    # Select the correct ebook URI
    ebook = list(g.subjects(RDF.type, PGTERMS.ebook))[0]

    publisher = get_text(ebook, DCTERMS.publisher)
    license = get_resource(ebook, DCTERMS.license)
    issued = get_text(ebook, DCTERMS.issued)
    rights = get_text(ebook, DCTERMS.rights)
    downloads = try_get_int(get_text(ebook, PGTERMS.downloads))

    creator_node = g.value(ebook, DCTERMS.creator)
    creator = Agent(
        name=get_text(creator_node, PGTERMS.name),
        birthdate=try_get_int(get_text(creator_node, PGTERMS.birthdate)),
        deathdate=try_get_int(get_text(creator_node, PGTERMS.deathdate)),
        aliases=[str(alias) for alias in g.objects(creator_node, PGTERMS.alias)],
        webpage=get_resource(creator_node, PGTERMS.webpage)
    )

    title = get_text(ebook, DCTERMS.title)
    description = get_text(ebook, PGTERMS.marc520)
    language = get_text(g.value(ebook, DCTERMS.language), RDF.value)
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
        extents = [try_get_int(str(e)) for e in g.objects(file_format, DCTERMS.extent)]
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
