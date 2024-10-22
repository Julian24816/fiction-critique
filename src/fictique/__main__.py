# setup openai from .env file
from dotenv import load_dotenv

from crawler import scrape_all_rankings_silent, scrape_all_rankings, download_complete_fiction_text, \
    remove_copyright_notes_from_file

load_dotenv()

from pathlib import Path
from scene_segmentation import segment_text


urls = {
    "best-rated": "https://www.royalroad.com/fictions/best-rated",
    "trending": "https://www.royalroad.com/fictions/trending",
    "ongoing": "https://www.royalroad.com/fictions/active-popular",
    #    "complete": "https://www.royalroad.com/fictions/complete",
    "weekly-popular": "https://www.royalroad.com/fictions/weekly-popular",
    #    "latest-update": "https://www.royalroad.com/fictions/latest-updates",
    #    "new": "https://www.royalroad.com/fictions/new",
    "rising-stars": "https://www.royalroad.com/fictions/rising-stars",
    #    "writathon": "https://www.royalroad.com/fictions/writathon",
}


if __name__ == "__main__":
    # scrape_all_rankings(urls)
    # scrape_all_rankings_silent(urls)


    download_complete_fiction_text(92144)
    remove_copyright_notes_from_file(Path(f"out/92144.md"))
    # scenes = segment_text(Path(f"out/82003.md"), verbosity=1)
    #     for i, scene in enumerate(scenes):
    #     with open(outdir / f"{i}.md", "w", encoding="utf-8") as f:
    #         f.write(scene.to_markdown())
    # outdir = Path(f"out/82003")
    # outdir.mkdir(exist_ok=True)
    #
    # for i in range(71): # outdir currently contains 71 scenes
    #     with (outdir / f"{i}.md").open(encoding="utf-8") as file:
    #         title = file.readline()[3:-1]
    #         file.readline()
    #         summary = file.readline()[9:-1]
    #     with (outdir / "summaries.md").open("a", encoding="utf-8") as file:
    #         file.write(f"# {i}. {title}\n{summary}\n\n")
