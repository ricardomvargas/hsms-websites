import re
import socket
import unicodedata
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

WIKI_API = "https://en.wikipedia.org/w/api.php"

# Words stripped from the company name before generating domain candidates.
# Only true legal entity suffixes and geography words that are virtually
# never part of the actual brand domain. Words like "Group", "International",
# "Global" are intentionally kept — they often appear in brand domains.
LEGAL_SUFFIXES = [
    r"\bb\.v\.?\b",
    r"\bn\.v\.?\b",
    r"\bltd\b",
    r"\binc\b",
    r"\bllc\b",
    r"\bgmbh\b",
    r"\bag\b",
    r"\bs\.a\.?\b",
    r"\bs\.l\.?\b",
    r"\bsarl\b",
    r"\bsas\b",
    r"\bcorp\b",
    r"\bco\b",
    r"\bnederland\b",
    r"\bnetherlands\b",
]

# TLDs are tried in this order for every candidate base.
# .nl is first since we target Dutch companies.
# .eu is second — common for European brands and often the correct
# choice when the company uses a ccTLD or a descriptive domain.
TLDS = [".nl", ".eu", ".com", ".net", ".org", ".io"]

# Keywords that indicate a domain is parked (not actively used).
# Includes both English and Dutch phrases.
PARKED_KEYWORDS = [
    "buy this domain",
    "domain is for sale",
    "this domain may be for sale",
    "domain parking",
    "hugedomains",
    "sedo.com",
    "afternic",
    "dan.com",
    "this domain is parked",
    "domain name is for sale",
    "buy this domain name",
    "domain available for purchase",
    "parked free",
    "domain name marketplace",
    "dit domein is te koop",
    "domeinnaam is te koop",
    "deze domeinnaam is te koop",
    "domein te koop",
    "koop dit domein",
    "dit domein wordt geparkeerd",
]

# Domain marketplaces that host parked pages. If a request redirects to one
# of these, the domain is almost certainly for sale / not actively used.
# These were removed from PARKED_KEYWORDS because they are checked against
# the final URL (resp.url) rather than the page content — some marketplaces
# serve minimal HTML that doesn't contain the domain name in the text.
PARKED_MARKETPLACES = [
    "hugedomains.com",
    "sedo.com",
    "afternic.com",
    "dan.com",
    "buythisdomain.com",
    "domainmarket.com",
    "undeveloped.com",
    "nichedomains.com",
    "brandbucket.com",
    "saw.com",
]


def _clean_name(name: str) -> str:
    """Normalize a company name into a domain-friendly slug.

    Steps:
    1. Lowercase
    2. Normalize accented chars to ASCII (Amélie → Amelie)
    3. Strip legal suffixes and "Nederland"/"Netherlands"
    4. Remove any remaining non-alphanumeric chars (except spaces/hyphens)
    5. Collapse whitespace
    """
    result = name.lower()
    result = unicodedata.normalize("NFKD", result)
    result = result.encode("ascii", "ignore").decode("ascii")
    for suffix in LEGAL_SUFFIXES:
        result = re.sub(suffix, "", result)
    result = re.sub(r"[^a-z0-9\s-]", "", result)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def _add_candidates(candidates: set[str], words: list[str]) -> None:
    """Add hyphenated and concatenated forms of the full word list and all
    its progressive prefixes (dropping trailing words one by one).

    For example, words=["a", "b", "c"] generates:
      a-b-c, abc, a-b, ab, a
    """
    for i in range(len(words), 0, -1):
        prefix = words[:i]
        candidates.add("-".join(prefix))
        candidates.add("".join(prefix))


def _generate_domains(name: str) -> list[str]:
    """Generate an ordered list of full domain names to try.

    Strategy:
    1. Clean the company name (strip suffixes, normalize accents)
    2. Generate base candidates from the cleaned words:
       - Full name: hyphenated and concatenated (e.g. "1-cube", "1cube")
       - Progressive prefixes: shorter variants (e.g. "1")
    3. Also generate a set of candidates with "Nederland"/"Netherlands"
       removed — these are often not part of the brand domain but can
       drown out more specific short names.
    4. Sort candidates:
       - Longest alphanumeric length first (more words = more specific)
       - Within same length, concatenated before hyphenated
       (brand domains usually omit hyphens)
    5. Append each TLD to every base candidate to produce the final list.
    """
    clean = _clean_name(name)
    if not clean:
        return []

    words = clean.split()
    candidates: set[str] = set()

    _add_candidates(candidates, words)

    # Generate an extra set of candidates without "Nederland"/"Netherlands".
    # This helps when the stripped word is part of the legal name but not
    # the brand, allowing shorter yet specific bases (e.g. "petiteamelie"
    # instead of "petite-amelie-nederland").
    filtered = [w for w in words if w not in ("nederland", "netherlands")]
    if filtered and filtered != words:
        _add_candidates(candidates, filtered)

    # Sort: longer (more specific) first, then fewer hyphens.
    # Within the same alphanumeric length, concatenated forms are preferred
    # because most companies use them (e.g. "1cube" over "1-cube").
    sorted_candidates = sorted(
        candidates,
        key=lambda b: (-len(b.replace("-", "")), b.count("-")),
    )

    domains: list[str] = []
    for base in sorted_candidates:
        for tld in TLDS:
            domains.append(f"{base}{tld}")

    return domains


def _dns_resolves(domain: str) -> bool:
    """Check if a domain has at least one DNS A record."""
    try:
        socket.setdefaulttimeout(5)
        socket.gethostbyname(domain)
        return True
    except (socket.gaierror, OSError):
        return False


def _follow_js_redirect(url: str, html: str) -> Optional[str]:
    """Check if the page contains a JS-based redirect and follow it.

    Some parked domains use JavaScript (window.location) or meta refresh
    to redirect to a marketplace after the page loads. Since requests
    doesn't execute JS, we detect common patterns and follow them here.
    """
    meta = re.search(
        # <meta http-equiv="refresh" content="2;url=...">
        r'<meta[^>]*?http-equiv\s*=\s*["\']?refresh'
        r'["\']?[^>]*?content\s*=\s*["\']\d+;\s*url=([^"\'> ]+)',
        html,
        re.IGNORECASE,
    )
    target = meta.group(1) if meta else None

    if not target:
        # JS redirect: window.location.href = "..." / window.location = "..."
        js = re.search(
            r'window\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']',
            html,
        )
        target = js.group(1) if js else None

    if target:
        absolute_url = urljoin(url, target)
        try:
            resp = requests.get(absolute_url, timeout=8, allow_redirects=True)
            return resp.url
        except requests.RequestException:
            return None

    return None


def _check_url(url: str) -> Optional[str]:
    """Fetch a URL and classify it as valid or parked.

    Returns the final URL (after redirects) if the page is not a parked
    domain, or None if:
    - The request failed
    - The final URL is a known parking marketplace
    - The page content contains parking keywords
    - A JS/meta refresh redirect leads to a known marketplace
    """
    try:
        resp = requests.get(url, timeout=8, allow_redirects=True)
        final_url = resp.url.lower()

        if any(mp in final_url for mp in PARKED_MARKETPLACES):
            return None

        text = resp.text.lower()
        if any(kw in text for kw in PARKED_KEYWORDS):
            return None

        # Check for JS or meta refresh redirects to marketplaces
        js_target = _follow_js_redirect(resp.url, resp.text)
        if js_target:
            js_target_lower = js_target.lower()
            if any(mp in js_target_lower for mp in PARKED_MARKETPLACES):
                return None

        return resp.url
    except requests.RequestException:
        return None


def _lookup_dns(company_name: str) -> Optional[str]:
    """Try to find a company's website by DNS-based candidate generation.

    For each generated domain (in priority order):
    1. Check if it resolves via DNS
    2. If yes, fetch the URL and check for parking keywords
    3. Return the first non-parked, reachable URL, or None if none found
    """
    for domain in _generate_domains(company_name):
        if not _dns_resolves(domain):
            continue
        url = f"https://{domain}"
        final = _check_url(url)
        if final:
            return final
    return None


def _lookup_wikipedia(company_name: str) -> Optional[str]:
    """Fallback: find a company's website via Wikipedia.

    Searches Wikipedia for the company name, parses the infobox on the
    first matching article, and extracts the "Website" field.
    """
    try:
        search_resp = requests.get(
            WIKI_API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": company_name,
                "format": "json",
                "srlimit": 3,
            },
            timeout=10,
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()
        pages = search_data.get("query", {}).get("search", [])
        if not pages:
            return None

        page_title = pages[0]["title"]

        parse_resp = requests.get(
            WIKI_API,
            params={
                "action": "parse",
                "page": page_title,
                "prop": "text",
                "section": 0,
                "format": "json",
            },
            timeout=10,
        )
        parse_resp.raise_for_status()
        html = parse_resp.json().get("parse", {}).get("text", {}).get("*", "")
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        th = soup.find("th", string=re.compile(r"website", re.IGNORECASE))
        if not th:
            return None

        td = th.find_parent("tr")
        if not td:
            return None

        link = td.find("a", href=True)
        if link and link["href"].startswith("http"):
            return link["href"]

    except requests.RequestException:
        return None


def find_website(company_name: str) -> Optional[str]:
    """Find a company's website URL using a two-step strategy.

    1. DNS lookup: generate domain candidates from the company name,
       resolve them, and check for parked domains.
    2. Wikipedia fallback: if DNS fails, search Wikipedia and parse
       the infobox for a website link.

    Returns the URL string or None if no website was found.
    """
    result = _lookup_dns(company_name)
    if result:
        return result
    return _lookup_wikipedia(company_name)


def find_websites(
    companies: list[dict[str, str]],
) -> dict[str, Optional[str]]:
    """Find websites for a batch of companies (max 20 per call).

    Accepts a list of dicts with "name" and "kvk_number" keys.
    Returns a dict mapping each kvk_number to its found URL or None.
    """
    results: dict[str, Optional[str]] = {}
    for company in companies[:20]:
        results[company["kvk_number"]] = find_website(company["name"])
    return results
