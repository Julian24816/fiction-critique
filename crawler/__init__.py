from serialization import save_fiction, update_ranking
from typing import MutableMapping, List, Tuple, Mapping

from .royalroad import scrape_fiction_list, Fiction

def scrape_all_rankings(
        key2url: Mapping[str, str],
        report_rankings_until: int = 3, report_multi_ranking: int = 2, verbose: bool = True
):
    fictions: MutableMapping[int, Fiction] = {}
    for key, url in key2url.items():
        if verbose: print("now scraping", url)
        scraped = scrape_fiction_list(url)

        # update rankings
        ranking = [f.slot for f in scraped]
        updated = update_ranking(key, ranking)
        if verbose: print("-", key, "ranking", "updated" if updated else "unchanged")

        # collect scraped novels
        new = 0
        for i, f in enumerate(scraped):
            if f.slot not in fictions:
                fictions[f.slot] = f
                new += 1
            f = fictions[f.slot]
            f.stats[f"ranking-{key}"] = i + 1
        if verbose: print("-", new, "of", len(scraped), "fictions not yet seen on rankings during this run")

        # report on top ranks:
        if report_rankings_until == 1:
            print(key, "leader:", scraped[0].slot, scraped[0].title)
        elif report_rankings_until > 1:
            print(key, "ranking:")
            for i in range(0, report_rankings_until):
                print(f"{i + 1}. {scraped[i].slot} {scraped[i].title}")

    if verbose: print("collected", len(fictions), "novels")
    num_updated = 0
    on_rankings: MutableMapping[int, List[Tuple[Fiction, List[str]]]] = {i: [] for i in range(len(key2url) + 1)}
    for f in fictions.values():
        if save_fiction(f):
            num_updated += 1
        rankings = list(i[8:] for i in filter(lambda item: item.startswith('ranking-'), f.stats))
        on_rankings[len(rankings)].append((f, rankings))
    if verbose: print("updated", num_updated)

    for i in range(len(key2url), report_multi_ranking - 1, -1):
        if len(on_rankings[i]) > 0:
            print("fictions on", i, "rankings:")
            for f, rankings in on_rankings[i]:
                print("-", f.slot, *rankings, "-", f.title)

def scrape_all_rankings_silent(key2url: Mapping[str, str]):
    scrape_all_rankings(
        key2url,
        report_rankings_until=0, report_multi_ranking=len(key2url)+1, verbose=False
    )