from pathlib import Path
from requests import HTTPError

from fictique.model import GutenbergBook
from fictique.crawler.gutenberg import download_rdf, download_text, parse_rdf
from fictique.serialization import save_as_yaml

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