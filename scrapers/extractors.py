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

def find_emails(html: str) -> set:
    """Extract valid emails from HTML using regex."""
    if not html:
        return set()
    
    # Standard email regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    raw_emails = set(re.findall(email_pattern, html))
    
    # Also extract emails from mailto: href attributes (strip query strings)
    soup_text = html  # regex already handles mailto content, but strip ?-params below
    
    # Filter out common false positives
    junk_local_parts = {'noreply', 'no-reply', 'donotreply', 'do-not-reply', 'postmaster',
                        'mailer-daemon', 'daemon', 'bounce', 'root', 'webmaster', 'hostmaster',
                        'abuse', 'spam', 'test', 'example', 'user', 'you', '_'}
    junk_keywords = ['sentry', 'example.com', 'example.org', 'yourcompany', 'yourdomain',
                     'domain.com', 'test@', 'placeholder']
    
    valid_emails = set()
    for email in raw_emails:
        email = email.lower()
        
        # Strip query-string suffixes that sneak in from mailto: hrefs
        if '?' in email:
            email = email.split('?')[0]
        
        # Must have a proper local part and domain
        if '@' not in email:
            continue
        local, domain_part = email.split('@', 1)
        
        # Skip very short or empty local parts
        if len(local) < 2:
            continue
        
        # Skip image file extensions
        if any(email.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
            continue
        
        # Skip junk local parts
        if local in junk_local_parts:
            continue
        
        # Skip junk keywords anywhere in the address
        if any(kw in email for kw in junk_keywords):
            continue
        
        # Domain must have a real TLD (at least one dot with 2+ char extension)
        parts = domain_part.split('.')
        if len(parts) < 2 or len(parts[-1]) < 2:
            continue
        
        valid_emails.add(email)
        
    return valid_emails
