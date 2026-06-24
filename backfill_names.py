"""
Backfill names for existing contacts in the DB that currently have 'Unknown' as name.
Uses infer_name_from_email() — personal-style emails get a real name,
role-based emails (sales@, info@) stay as 'Unknown'.
"""
import asyncio
from sqlalchemy import select
from core.database import get_db
from core.models import Contact
from services.enrichment import infer_name_from_email

async def backfill_names():
    updated = 0
    async for db in get_db():
        result = await db.execute(select(Contact))
        contacts = result.scalars().all()

        for contact in contacts:
            current_name = (contact.name or "").strip()
            if current_name in {"Unknown", ""}:
                inferred = infer_name_from_email(contact.email)
                if inferred:
                    print(f"  {contact.email:45s}  '{current_name}' -> '{inferred}'")
                    contact.name = inferred
                    updated += 1
                # else: no name can be inferred — leave as Unknown

        await db.commit()
        print(f"\nName backfill complete. Updated {updated} contacts.")

if __name__ == "__main__":
    asyncio.run(backfill_names())
