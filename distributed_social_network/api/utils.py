import re

def get_uuid_from_url(url):
    p = "([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})"
    pattern = re.compile(p, re.IGNORECASE)
    return pattern.search(url).group()