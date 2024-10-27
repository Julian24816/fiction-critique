from pathlib import Path
import subprocess

from fictique.crawler import scrape_fiction, scrape_chapter
from fictique.model import Fiction


def download(fid: int, folder: Path) -> (Path, Fiction):
    path = folder / f"{fid}.md"
    last_saved_chapter = -1
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            last_saved_chapter = int(f.read().split("## ")[-1].split(".")[0])

    fiction = scrape_fiction(fid)
    print("downloaded metadata")

    if last_saved_chapter == -1:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {fiction.title}\n\n")
            f.write(f"by {fiction.author}\n\n")
            f.write(fiction.description)
            f.write("\n\n")

    with open(path, "a", encoding="utf-8") as f:
        for i, cid in enumerate(fiction.chapters):
            if i < last_saved_chapter:
                continue
            chapter = scrape_chapter(fid, cid)
            f.write(f"## {i+1}. {chapter.title}\n\n")
            f.write(chapter.body)
            f.write("\n\n")
            print("downloaded chapter", i+1, "of", len(fiction.chapters))

    return path, fiction

import re

def to_snake_case(text):
    """
    Converts a given text to snake_case.

    Parameters:
    text (str): The text to convert.

    Returns:
    str: The snake_case version of the text.
    """
    # Replace non-letter and non-digit characters with underscores
    text = re.sub(r'[^a-zA-Z0-9]', '_', text)

    # Convert camelCase or PascalCase to snake_case
    text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)

    # Convert the entire text to lowercase
    return text.lower()


if __name__ == '__main__':
    directory = Path("data/royalroad")
    directory.mkdir(parents=True, exist_ok=True)
    textpath, metadata = download(81642, directory)

    # todo split into multiple files, e.g. every 100 chapters
    command = [
        "pandoc",
        textpath,
        "-o", directory / f"{to_snake_case(metadata.title)}.epub",
        "--metadata", f'title="{metadata.title}"',
        "--metadata", f'author="{metadata.author}"',
        "--metadata", 'lang=en-US',
        "--metadata", f'series="{metadata.title}"',
        "--metadata", 'series_index="1"',
        "--split-level=1"
    ]

    # Execute the command
    subprocess.run(command, check=True)
    print("converted to epub")
