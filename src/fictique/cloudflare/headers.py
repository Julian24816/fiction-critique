import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from time import sleep

cloudflare_headers = {}

def get_cloudflare_headers(url):
    key = get_scheme_and_hostname(url)
    if key not in cloudflare_headers:
        cloudflare_headers[key] = create_cloudflare_headers(key)
    return cloudflare_headers[key]

def get_scheme_and_hostname(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    hostname = parsed_url.hostname
    return f"{scheme}://{hostname}"

def create_cloudflare_headers(url):
    """inspired by https://github.com/EL-S/RoyalRoadAPI/blob/fd81d396777c89fb34d4165c9f274204c5f97610/royalroadlapi.py#L929"""
    if not check_for_cloudflare_headers_and_content(url)[1]:
        return {}
    window_size = "1280,720"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % window_size)
    chrome_options.add_argument("user-agent="+user_agent)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = Chrome(chrome_options)
    driver.get(url)
    driver.get_screenshot_as_file("out/cloudflare-capture.png")
    sleep(10)
    cookies = " ".join([c["name"]+"="+c["value"]+";" for c in driver.get_cookies()])
    headers = {"user-agent":user_agent, "cookie":cookies}
    driver.close()
    return headers

def check_for_cloudflare_headers_and_content(url):
    response = requests.get(url)

    has_cloudflare_headers = any(header in response.headers for header in [
        'cf-ray',
        'cf-cache-status',
        'cf-request-id',
        'cf-bgj',
    ])

    soup = BeautifulSoup(response.text, 'html.parser')
    has_cloudflare_content = \
        soup.find('form', id='challenge-form') is not None or \
        soup.find('div', class_='cf-error-overview') is not None

    return has_cloudflare_headers, has_cloudflare_content


def is_cloudflare_protected_url(url):
    return check_for_cloudflare_headers_and_content(url)[0]