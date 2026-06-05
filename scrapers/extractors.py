import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    """Extract the clean domain from a full URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower().strip()
    except Exception:
        return url

def clean_text(html: str) -> str:
    """Extract clean text from raw HTML."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def find_social_links(html: str) -> dict:
    """Find Twitter and LinkedIn links within HTML."""
    links = {"twitter": None, "linkedin": None}
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if "twitter.com" in href or "x.com" in href:
            links["twitter"] = a["href"]
        elif "linkedin.com/company" in href:
            links["linkedin"] = a["href"]
    return links
