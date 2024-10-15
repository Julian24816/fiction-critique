from crawler import scrape_all_rankings_silent, scrape_all_rankings
from crawler.royalroad import scrape_fiction, scrape_chapter

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

def download_complete_fiction(slot: int, verbose: bool = True):
    fiction = scrape_fiction(slot)
    if verbose: print("scraped fiction:", fiction.title, "-", len(fiction.chapters), "chapters")
    with open(f"out/{slot}.md", "w", encoding="utf-8") as f:
        f.write(f"# {fiction.title}\n\n")
        f.write(f"by {fiction.author}\n\n")
        f.write(fiction.description)
        f.write("\n\n")

        for c in (scrape_chapter(slot, i) for i in fiction.chapters):
            f.write(f"## {c.title}\n\n")
            f.write(c.body)
            f.write("\n\n")
            if verbose: print("scraped chapter:", c.title)


if __name__ == "__main__":
    # scrape_all_rankings(urls)
    # scrape_all_rankings_silent(urls)

    # 82003: john boy's big boy
    # 89228: ruinous return
    download_complete_fiction(89228)
