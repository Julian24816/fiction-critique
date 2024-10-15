from crawler import scrape_all_rankings_silent
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


if __name__ == "__main__":
    # scrape_all_rankings_silent(urls)
    jbbb = scrape_fiction(82003)
    chapters = [scrape_chapter(jbbb.slot, i) for i in jbbb.chapters]
    with open("out/jbbb.md", "w", encoding="utf-8") as f:
        for chapter in chapters:
            f.write(f"# {chapter.title}")
            f.write("\n")
            f.write(chapter.body)
            f.write("\n\n")
    print("wrote all chapters of jbbb to output")