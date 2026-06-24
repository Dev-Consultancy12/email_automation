import re
import asyncio
from urllib.parse import urljoin, urlparse
from collections import deque

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

from core.database import AsyncSessionLocal
from core.models import Company, Contact


EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

MAX_PAGES = 15

KEYWORDS = [
    "contact",
    "about",
    "team",
    "leadership",
    "company",
    "privacy",
    "support"
]


def get_html(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.text

    except Exception as e:
        print(f"Error opening {url}: {e}")

    return None


def extract_emails(soup):
    found = set()

    text = soup.get_text(
        separator=" "
    )

    emails = re.findall(
        EMAIL_REGEX,
        text
    )

    for email in emails:
        email = email.lower()

        ignore = [
            ".png",
            ".jpg",
            ".jpeg",
            ".svg",
            ".webp"
        ]

        if not any(
            ext in email
            for ext in ignore
        ):
            found.add(email)

    for tag in soup.find_all(
        "a",
        href=True
    ):
        href = tag["href"]

        if href.startswith(
            "mailto:"
        ):
            email = href.replace(
                "mailto:",
                ""
            ).strip()

            found.add(
                email.lower()
            )

    return found


def get_internal_links(
    soup,
    base_url
):
    links = set()

    base_domain = urlparse(
        base_url
    ).netloc

    for tag in soup.find_all(
        "a",
        href=True
    ):
        href = tag["href"]

        full_url = urljoin(
            base_url,
            href
        )

        parsed = urlparse(
            full_url
        )

        if (
            parsed.netloc
            == base_domain
        ):
            if any(
                keyword
                in full_url.lower()
                for keyword
                in KEYWORDS
            ):
                links.add(
                    full_url
                )

    return links


def scrape_company(
    website
):
    queue = deque(
        [website]
    )

    visited = set()

    all_emails = set()

    pages_scanned = 0

    while (
        queue
        and pages_scanned
        < MAX_PAGES
    ):
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        print(
            f"Scanning: {url}"
        )

        html = get_html(
            url
        )

        if not html:
            continue

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        emails = extract_emails(
            soup
        )

        all_emails.update(
            emails
        )

        links = get_internal_links(
            soup,
            website
        )

        for link in links:
            if link not in visited:
                queue.append(
                    link
                )

        pages_scanned += 1

    return list(
        all_emails
    )


async def save_to_database(
    website,
    emails
):
    async with AsyncSessionLocal() as db:

        domain = urlparse(
            website
        ).netloc.replace(
            "www.",
            ""
        )

        result = await db.execute(
            select(Company).where(
                Company.domain == domain
            )
        )

        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                name=domain.split(".")[0].title(),
                domain=domain,
                source="website_scraper"
            )

            db.add(company)

            await db.commit()
            await db.refresh(company)

            print(
                f"Company saved: {domain}"
            )

        saved_count = 0

        for email in emails:

            result = await db.execute(
                select(Contact).where(
                    Contact.email
                    == email
                )
            )

            existing = (
                result.scalar_one_or_none()
            )

            if existing:
                continue

            

            name = email.split("@")[0]

            name = (
                name.replace(".", " ")
                    .replace("_", " ")
                    .replace("-", " ")
                    .title()
            )

            role = "General"

            email_lower = email.lower()

            if "sales" in email_lower:
                role = "Sales"
                name = "Sales Team"

            elif "support" in email_lower:
                role = "Support"
                name = "Support Team"

            elif "privacy" in email_lower:
                role = "Privacy"
                name = "Privacy Team"

            elif "security" in email_lower:
                role = "Security"
                name = "Security Team"

            elif "dpo" in email_lower:
                role = "Data Protection Officer"
                name = "DPO"

            elif "ceo" in email_lower:
                role = "CEO"

            elif "cto" in email_lower:
                role = "CTO"

            elif "founder" in email_lower:
                role = "Founder"

            contact = Contact(
                company_id=company.id,
                name=name,
                email=email,
                role=role
            )

            db.add(contact)

        saved_count += 1

        await db.commit()

        print(
            f"Saved {saved_count} emails"
        )


async def main():
    website = input(
        "Enter company website: "
    )

    emails = scrape_company(
        website
    )

    print(
        "\nFound Emails:"
    )

    for email in emails:
        print(email)

    await save_to_database(
        website,
        emails
    )


if __name__ == "__main__":
    asyncio.run(main())