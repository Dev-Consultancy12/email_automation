"""
One-time cleanup script.
Removes:
  - Mock contacts (Jane Doe / John Smith) inserted by the old enrichment fallback
  - Contacts with malformed emails (e.g. contain '?', empty domain, no TLD)
  - Contacts with obvious placeholder emails (you@domain.com, _@...)
  - Orphaned EmailStatus rows are cascade-deleted via FK
"""

import asyncio
from sqlalchemy import select, delete
from core.database import get_db
from core.models import Contact, EmailStatus

JUNK_NAMES = {"Jane Doe", "John Smith"}
JUNK_LOCAL_PARTS = {"jane.doe", "john.smith", "you", "_"}
JUNK_DOMAINS = {"domain.com", "example.com", "example.org"}


def is_bad_email(email: str) -> bool:
    if not email or "@" not in email:
        return True
    # Contains query string from mailto: href
    if "?" in email:
        return True
    local, domain = email.split("@", 1)
    # Empty or junk local part
    if local in JUNK_LOCAL_PARTS or len(local) < 2:
        return True
    # Junk domain
    if domain in JUNK_DOMAINS:
        return True
    # No proper TLD
    parts = domain.split(".")
    if len(parts) < 2 or len(parts[-1]) < 2:
        return True
    return False


async def cleanup():
    removed = 0
    async for db in get_db():
        result = await db.execute(select(Contact))
        contacts = result.scalars().all()

        for contact in contacts:
            should_delete = False
            reason = ""

            # Check for fake mock names
            if contact.name and contact.name.strip() in JUNK_NAMES:
                should_delete = True
                reason = f"mock name '{contact.name}'"

            # Check for bad email
            if not should_delete and is_bad_email(contact.email):
                should_delete = True
                reason = f"bad email '{contact.email}'"

            if should_delete:
                print(f"  Removing contact [{contact.email}] — {reason}")
                # Delete EmailStatus first (no cascade on this model)
                await db.execute(
                    delete(EmailStatus).where(EmailStatus.contact_id == contact.id)
                )
                await db.delete(contact)
                removed += 1

        await db.commit()
        print(f"\nCleanup complete. Removed {removed} bad contacts.")


if __name__ == "__main__":
    asyncio.run(cleanup())
