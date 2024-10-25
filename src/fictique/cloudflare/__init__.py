from .emails import is_cloudflare_protected_email, decode_all_emails
from .headers import get_cloudflare_headers
from tornado.httpclient import HTTPClient, HTTPError
from bs4 import BeautifulSoup

__all__ = [
    "fetch_as_soup"
]

def fetch_as_soup(url: str) -> BeautifulSoup:
    client = HTTPClient()
    try:
        html = client.fetch(url, headers=get_cloudflare_headers(url)).body.decode('utf-8') #decode the html response
        soup = BeautifulSoup(html, "lxml") #parse the html
        if soup.find(is_cloudflare_protected_email): #remove protected emails by cloudflare
            soup = decode_all_emails(soup)
        return soup #return the soup object
    except HTTPError as e: #if the http request fails
        print("HTTPError", e)
        raise e

