from typing import List


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.5",
    "Accept-Encoding": "gzip, deflate"
}


BASE_URL = "https://www.stepstone.de/jobs"

# search settings
CITIES = ["Würzburg"]  # type: List[str]
RADIUS = 5      # type: int
SEARCH_PAGES_UNTIL = 1  #type: int
STELLENANGEBOTE_REGEX = r'href="([^"]*\/stellenangebote-[^\s"]+)"'

VALUES = {
    "introduction": "section-text-introduction-content",
    "description": "section-text-description-content",
    "profile": "section-text-profile-content",
    "benefits": "section-text-benefits-content"
}