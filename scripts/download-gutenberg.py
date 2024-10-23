from dataclasses import dataclass, asdict
from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from typing import List
import requests
import yaml
from requests import HTTPError


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

def save_as_yaml(book: GutenbergBook, directory: Path, book_id: int) -> Path:
    yaml_filepath = directory / f'{book_id}.yaml'
    with open(yaml_filepath, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(asdict(book), yaml_file, default_flow_style=False, allow_unicode=True)
    return yaml_filepath

def download_metadata_and_text(book_id: int, directory: Path) -> GutenbergBook:
    rdf_path = download_rdf(book_id, directory)
    try:
        download_text(book_id, directory)
    except HTTPError as e:
        download_text(book_id, directory, False)
    metadata = parse_rdf(rdf_path)
    save_as_yaml(metadata, directory, book_id)
    return metadata

if __name__ == "__main__":
    gut_dir = Path("data/gutenberg")
    gut_dir.mkdir(parents=True, exist_ok=True)
    for b in (
            35,  # The Time Machine
            36,  # The War of the Worlds
            41,  # The Legend of Sleepy Hollow
            43,  # The Strange Case of Dr. Jekyll and Mr. Hyde
            62,  # A Princess of Mars
            100,  # collected works of shakespeare
            135,  # Les Misérables
            209,  # The Turn of the Screw
            215,  # The Call of the Wild
            696,  # The Castle of Otranto
            768,  # Wuthering Heights
            996,  # Don Quixote
            1184,  # The Count of Monte Cristo
            1661,  # The Adventures of Sherlock Holmes
            1666,  # The Golden Asse
            2701,  # Moby Dick
            1251,  # Le Morte d’Arthur (Vol 1)
            1952,  # The Yellow Wallpaper
            11000,  # An Old Babylonian Version of the Gilgamesh Epic
            13268,  # Hindu literature : Comprising The Book of good counsels, Nala and Damayanti, The Ramayana, and Sakoontala
            16328,  # Beowulf
            19033,  # Alice's Adventures in Wonderland
            19942,  # Candide
            21765,  # Metamorphoses (1-7)
            22120,  # The Canterbury Tales
            22456,  # The Aeneid
            23700,  # The Decameron
            26740,  # The Picture of Dorian Gray
            34206,  # The Thousand and One Nights (Vol 1)
            42324,  # frankenstein
            42537,  # The Divine Comedy
            42671,  # pride and prejudice
            43936,  # The Wonderful Wizard of Oz
            45839,  # Dracula
            49487,  # Anna Karenina
            58585,  # The Prophet
            58866,  # The Murder on the Links
            59254,  # The Inimitable Jeeves
            59306,  # The Iliad & The Odyssey
            59437,  # A Son at the Front
            59794,  # The World Crisis
            61077,  # The King of Elfland's Daughter
            61221,  # A Passage to India
            64317,  # The Great Gatsby
            65473,  # Gulliver's Travels
            66057,  # The Tale of Genji
            67098,  # Winnie-the-Pooh
            67138,  # The Sun Also Rises
            68283,  # The Call of Cthulhu
            70271,  # When We Were Very Young
            70841,  # Robinson Crusoe
            70875,  # Arrowsmith
            71865,  # Mrs. Dalloway
    ):
        if (gut_dir / f"{b}.yaml").exists():
            continue
        try:
            meta = download_metadata_and_text(b, gut_dir)
            print("downloaded", b, meta.title)
        except HTTPError as e:
            print("failed to download", b, e)