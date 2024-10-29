from pathlib import Path

from tornado.httpclient import HTTPClientError
import re
import requests
import shlex
import subprocess
import time

from fictique.crawler import scrape_fiction, scrape_chapter
from fictique.model import Fiction


def with_retry(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except HTTPClientError as e:
        print("caught http client error, waiting 60s, then retrying...")
        time.sleep(60)
        return func(*args, **kwargs)


def download(fid: int, folder: Path) -> (Fiction, list[str], Path):
    fiction = with_retry(scrape_fiction, fid)
    print("downloaded metadata of", fid, fiction.title)

    image_url = fiction.image_url
    image_path = folder / f"{fid}.jpg"
    response = requests.get(image_url)
    with open(image_path, "wb") as img_file:
        img_file.write(response.content)
    print("downloaded cover image to", image_path)

    chapters = []

    for i, cid in enumerate(fiction.chapters):
        chapter = with_retry(scrape_chapter, fid, cid)
        chapters.append(f"## {i + 1}. {chapter.title}\n\n{chapter.body}\n\n")
        print("downloaded chapter", i + 1, "of", len(fiction.chapters))

    return fiction, chapters, image_path


def clean_title(title):
    # Remove everything inside and including brackets and parentheses
    title = re.sub(r'[\[\(].*?[\]\)]', '', title)
    # Remove special characters except whitespaces
    title = re.sub(r'[^\w\s]', '', title)
    # Remove leading and trailing whitespaces
    title = title.strip()
    # Replace any sequence of whitespace with a single space
    title = re.sub(r'\s+', ' ', title)
    return title


def escape_if_needed(value):
    value = str(value)
    # Escapes the value only if it contains whitespace
    return shlex.quote(value) if ' ' in value else value


def split_into_volumes(chapters, max_chapters=100):
    for i in range(0, len(chapters), max_chapters):
        yield chapters[i:i + max_chapters]


def convert_to_epub(volumes: list[list[str]], meta: Fiction, image_path: Path, output_dir: Path):
    for vol_num, chapters in enumerate(volumes, start=1):
        filename = clean_title(f"{meta.title} Volume {vol_num}")
        volume_path = output_dir / f"{filename}.md"
        with open(volume_path, "w", encoding="utf-8") as f:
            f.write(f"# {meta.title}\n\n")
            f.write(f"by {meta.author}\n\n")
            f.write(meta.description)
            f.write("\n\n")
            f.write("\n\n".join(chapters))

        command = [
            "pandoc",
            volume_path,
            "-o", output_dir / f"{filename}.epub",
            "--metadata", f'title="{filename}',
            "--metadata", f'author={escape_if_needed(meta.author)}',
            "--metadata", 'lang=en-US',
            "--metadata", f'series="{escape_if_needed(clean_title(meta.title))}"',
            "--metadata", f'series_index="{vol_num}"',
            "--split-level=2",
            "--epub-cover-image", image_path,
        ]
        subprocess.run(command, check=True)
        print(f"Converted to EPUB:", volume_path)


if __name__ == '__main__':
    directory = Path("data/royalroad")
    directory.mkdir(parents=True, exist_ok=True)

    for i in (#54068, 79092,
            76389, 70915, ):
        fiction, chapters, image_path = download(i, directory)
        volumes = list(split_into_volumes(chapters))
        convert_to_epub(volumes, fiction, image_path, directory)
