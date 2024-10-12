from cloudflare import fetch_as_soup


def get_fictions_from_url(url):
    soup = fetch_as_soup(url)
    fictions = []
    fiction_listings = soup.findAll("div", attrs={"class":"fiction-list-item"})
    for fiction_listing in fiction_listings:
        title_element = fiction_listing.find("h2")
        fiction_id = title_element.find("a").get("href").split("/")[-2].strip()
        title = title_element.text.strip().split("\n")[0]
        description = fiction_listing.find(id="description-" + fiction_id)
        fictions.append([fiction_id,title,description])
    return fictions
