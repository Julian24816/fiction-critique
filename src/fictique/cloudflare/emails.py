def is_cloudflare_protected_email(tag):
    """predicate to use in the beautifulsoup.find methods"""
    return tag.has_attr('data-cfemail')

def decode_all_emails(soup):
    for email in soup.find_all(is_cloudflare_protected_email):
        email.replaceWith(decode_cloudflare_protected_email(email.get("data-cfemail")))
    return soup

def decode_cloudflare_protected_email(data_string):
    """algorithm from https://github.com/EL-S/RoyalRoadAPI/blob/fd81d396777c89fb34d4165c9f274204c5f97610/royalroadlapi.py#L916"""
    email = ""
    r = int(data_string[:2], 16)
    i = 2
    while len(data_string)-i:
        char = int(data_string[i:i+2], 16) ^ r
        email += chr(char)
        i += 2
    return email