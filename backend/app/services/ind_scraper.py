import requests
from bs4 import BeautifulSoup

IND_URL = "https://ind.nl/en/public-register-recognised-sponsors/public-register-work"


def fetch_sponsors():
    response = requests.get(IND_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    if not table:
        raise ValueError("Could not find the sponsors table on the IND page")

    sponsors = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            name = cells[0].get_text(strip=True)
            kvk = cells[1].get_text(strip=True)
            if name and kvk:
                sponsors.append({"name": name, "kvk_number": kvk})

    return sponsors
