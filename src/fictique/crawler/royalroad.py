from bs4.element import Tag
from datetime import datetime
from fictique.cloudflare import fetch_as_soup
from fictique.model import Fiction, FictionStats
from fictique.model.chapter import Chapter
from html2text import HTML2Text


def scrape_fiction_list(url: str):
    """Note: currently only parses the first page of results"""
    return [parse_fiction_listing(l) for l in
        fetch_as_soup(url).findAll("div", attrs={"class": "fiction-list-item"})]


def parse_fiction_listing(tag: Tag) -> Fiction:
    """parses the contents of a div.fiction-listing-item on royalroad.com"""
    fiction_id = tag.find("h2").find("a").get("href").split("/")[-2].strip()
    return Fiction(
        slot=int(fiction_id),
        title=tag.find("h2").text.strip().split("\n")[0],
        author="",
        description=HTML2Text().handle(tag.find(id="description-" + fiction_id).prettify()),
        tags=[el.text for el in tag.find_all("a", attrs={"class": "fiction-tag"})],
        stats=parse_stats(tag.find("div", attrs={"class": "stats"})),
        chapters=[],
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


def scrape_fiction(slot: int) -> Fiction | None:
    url = f"https://www.royalroad.com/fiction/{slot}"
    soup = fetch_as_soup(url)
    if soup.find('div', attrs={'class': 'number font-red-sunglo'}):
        # if this element exists, the provided fiction slot is in-active
        # inspired by https://github.com/EL-S/RoyalRoadAPI/blob/fd81d396777c89fb34d4165c9f274204c5f97610/royalroadlapi.py#L535
        return None

    content = soup.find("div", attrs={"class":"page-content-inner"})
    title = content.find("h1").text.strip()
    author = content.find("h4", class_="font-white").find("a").text.strip()
    description = HTML2Text().handle(content.find("div", class_="description").prettify())
    tags = [tag.text.strip() for tag in soup.find_all('a', class_='fiction-tag')]

    # Extract image URL
    image_url = soup.find('meta', property='og:image')['content']

    # Extract stats
    stats = {}
    stats_section = soup.find('div', class_='fiction-stats')
    if stats_section:
        lists = stats_section.find_all('ul', class_='list-unstyled')
        for ul in lists:
            items = ul.find_all('li')
            for i in range(0, len(items), 2):
                key = items[i].text.strip(':').strip()
                if i + 1 < len(items):
                    value = items[i + 1].text.strip()
                    if items[i + 1].span is not None and 'aria-label' in items[i + 1].span.attrs:
                        value = float(items[i + 1].span['aria-label'].strip().split(' ')[0])
                    stats[key] = value

    # Extract chapters
    chapters = []
    for url in (tag.get("data-url") for tag in soup.findAll('tr', attrs={'style': 'cursor: pointer'})):
        chapters.append(int(url.split("/")[-2]))

    return Fiction(
        slot=slot,
        title=title,
        author=author,
        description=description,
        image_url=image_url,
        tags=tags,
        stats=stats,
        chapters=chapters
    )

def scrape_chapter(fiction_slot: int, chapter_slot: int) -> Chapter:
    url = f"https://www.royalroad.com/fiction/{fiction_slot}/chapter/{chapter_slot}"
    soup = fetch_as_soup(url)
    title = soup.find("h1").text.strip()
    body = HTML2Text().handle(soup.find("div", class_="chapter-content").prettify())
    return Chapter(title, body, slot=chapter_slot, fiction=fiction_slot)