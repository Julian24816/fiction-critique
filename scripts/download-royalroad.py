from pathlib import Path

from fictique.crawler import scrape_fiction, scrape_chapter

def download(fid: int, folder: Path) -> Path:
    path = folder / f"{fid}.md"
    with open(path, "w", encoding="utf-8") as f:
        fiction = scrape_fiction(fid)
        f.write(f"#{fiction.title}\n\n")
        f.write(f"by {fiction.author}\n\n")
        f.write(fiction.description)
        f.write("\n\n")
        print("downloaded metadata")

        for i, cid in enumerate(fiction.chapters):
            chapter = scrape_chapter(fid, cid)
            f.write(f"## {i+1}. {chapter.title}\n\n")
            f.write(chapter.body)
            f.write("\n\n")
            print("downloaded chapter", i+1, "of", len(fiction.chapters))

    return path

if __name__ == '__main__':
    directory = Path("data/royalroad")
    directory.mkdir(parents=True, exist_ok=True)
    textpath = download(81642, directory)
