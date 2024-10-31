from typing import Set
from collections import Counter

from fictique.crawler import scrape_all_rankings
from fictique.serialization import read_ranking, load_fiction

# URLs for scraping
urls = {
    "best-rated": "https://www.royalroad.com/fictions/best-rated",
    "trending": "https://www.royalroad.com/fictions/trending",
    "ongoing": "https://www.royalroad.com/fictions/active-popular",
    "weekly-popular": "https://www.royalroad.com/fictions/weekly-popular",
    "rising-stars": "https://www.royalroad.com/fictions/rising-stars",
}

# Scrape the rankings
scrape_all_rankings(urls, verbosity=1, report_rankings_until=0, report_multi_ranking=len(urls) + 1)

# Accumulate the tags
look_at: Set[int] = set(item for ranking in (
    read_ranking(key)[1] for key in urls
) for item in ranking)
tags_by_fiction = {slot: load_fiction(slot).tags for slot in look_at}

# Count the tags using Counter
tag_counts = Counter([tag for tags in tags_by_fiction.values() for tag in tags])

# Print the most common tags in a better format
print("\nMost Common Tags:")
for tag, count in tag_counts.most_common()[:10]:
    print(f"{tag}: {count}")


# Now focus on these tags
focus_tags = (
    "Adventure",
    "Action",
    "Fantasy",
    "LitRPG",
    "Magic",
    "Portal Fantasy / Isekay",
    "Progression",
)

sorted_fictions = sorted(
    tags_by_fiction.items(),
    key=lambda item: sum(1 for tag in item[1] if tag in focus_tags),
    reverse=True
)

print(f"\nFictions sorted by number of matching focus tags ({", ".join(focus_tags)}):\n")
for slot, tags in sorted_fictions[:10]:
    matching = sum(1 for tag in tags if tag in focus_tags)
    fiction = load_fiction(slot)
    print("##", matching, "matching tags:", fiction.title)
    print(fiction.description)
    print()
