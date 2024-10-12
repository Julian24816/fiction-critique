import html2text
from crawler import get_fictions_from_url

urls = {
    "weekly-popular": "https://www.royalroad.com/fictions/weekly-popular"
}

popular_fictions = get_fictions_from_url(urls["weekly-popular"])
converter = html2text.HTML2Text()
with open("out/weekly-popular.md", "w") as f:
    for fiction in popular_fictions:
        desc = converter.handle(fiction[2].prettify())
        f.write(f"# [{fiction[0]}] {fiction[1]}\n\n{desc}\n\n")

print(f"wrote {len(popular_fictions)} results to output")


