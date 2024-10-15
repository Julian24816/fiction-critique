from crawler import scrape_all_rankings_silent
from serialization import load_fiction

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
    print(load_fiction(94872))