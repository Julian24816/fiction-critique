from bs4 import Tag
from cloudflare import fetch_as_soup
from html2text import HTML2Text
from datetime import datetime
from .fiction import Fiction, FictionStats


def get_fictions_from_url(url):
    """Note: currently only parses the first page of results"""
    return [parse_fiction_listing(l) for l in
        fetch_as_soup(url).findAll("div", attrs={"class": "fiction-list-item"})]


def parse_fiction_listing(tag: Tag) -> Fiction:
    """parses the contents of a div.fiction-listing-item on royalroad.com"""
    fiction_id = tag.find("h2").find("a").get("href").split("/")[-2].strip()
    return Fiction(
        slot=int(fiction_id),
        title=tag.find("h2").text.strip().split("\n")[0],
        tags=[el.text for el in tag.find_all("a", attrs={"class": "fiction-tag"})],
        stats=parse_stats(tag.find("div", attrs={"class": "stats"})),
        description=HTML2Text().handle(tag.find(id="description-" + fiction_id).prettify())
    )


def parse_stats(tag: Tag) -> FictionStats:
    """parses the contents of a div.stats on royalroad.com"""
    parse_int = lambda x: int(x.replace(",",""))
    stats = list(tag.find_all("div", attrs={"class": "col-sm-6"}))
    return {
        "followers": parse_int(stats[0].find("span").text.split(" ")[0]),
        "rating": float(stats[1].get("aria-label").split(" ")[1]),
        "pages": parse_int(stats[2].find("span").text.split(" ")[0]),
        "views": parse_int(stats[3].find("span").text.split(" ")[0]),
        "chapters": parse_int(stats[4].find("span").text.split(" ")[0]),
        "last_updated": datetime.fromtimestamp(int(stats[5].find("time").get("unixtime")))
    }
