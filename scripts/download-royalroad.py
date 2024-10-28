from pathlib import Path
from tornado.httpclient import HTTPClientError
import re
import requests
import subprocess
import time

from fictique.crawler import scrape_fiction, scrape_chapter
from fictique.model import Fiction


def with_retry(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except HTTPClientError as e:
        print("caught http client error, waiting 10s, then retrying...")
        time.sleep(10)
        return func(*args, **kwargs)


def download(fid: int, folder: Path) -> (Fiction, list[str], Path):
    fiction = with_retry(scrape_fiction, fid)
    print("downloaded metadata")

    image_url = fiction.image_url
    image_path = folder / f"{fid}.jpg"
    response = requests.get(image_url)
    with open(image_path, "wb") as img_file:
        img_file.write(response.content)
    print("downloaded image", image_path)

    chapters = []

    for i, cid in enumerate(fiction.chapters):
        chapter = with_retry(scrape_chapter, fid, cid)
        chapters.append(f"## {i + 1}. {chapter.title}\n\n{chapter.body}\n\n")
        print("downloaded chapter", i + 1, "of", len(fiction.chapters))

    return fiction, chapters, image_path


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


def split_into_volumes(chapters, max_chapters=100):
    for i in range(0, len(chapters), max_chapters):
        yield chapters[i:i + max_chapters]


def convert_to_epub(volumes: list[list[str]], meta: Fiction, image_path: Path, output_dir: Path):
    for vol_num, volume in enumerate(volumes, start=1):
        volume_path = output_dir / f"{to_snake_case(meta.title)}_volume_{vol_num}.md"
        with open(volume_path, "w", encoding="utf-8") as f:
            f.write(f"# {meta.title}\n\n")
            f.write(f"by {meta.author}\n\n")
            f.write(meta.description)
            f.write("\n\n")
            f.write("\n\n".join(volume))

        command = [
            "pandoc",
            volume_path,
            "-o", output_dir / f"{to_snake_case(meta.title)}_volume_{vol_num}.epub",
            "--metadata", f'title="{meta.title}" (Volume {vol_num})',
            "--metadata", f'author="{meta.author}"',
            "--metadata", 'lang=en-US',
            "--metadata", f'series="{meta.title}"',
            "--metadata", f'series_index="{vol_num}"',
            "--split-level=1",
            "--epub-cover-image", image_path
        ]
        subprocess.run(command, check=True)
        print(f"Converted to EPUB: Volume {vol_num}")


if __name__ == '__main__':
    directory = Path("data/royalroad")
    directory.mkdir(parents=True, exist_ok=True)

    for i in (#88515, 83023,
            82768, ):
        fiction, chapters, image_path = download(i, directory)
        volumes = list(split_into_volumes(chapters))
        convert_to_epub(volumes, fiction, image_path, directory)
