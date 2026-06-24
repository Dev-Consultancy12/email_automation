"""
Backfill roles for existing contacts in the DB that have Generic/Unknown roles.
Uses the same infer_role_from_email() logic so existing data is updated consistently.
"""
import asyncio
from sqlalchemy import select
from core.database import get_db
from core.models import Contact
from services.enrichment import infer_role_from_email

ROLES_TO_UPDATE = {"General", "General Contact", None, ""}

async def backfill_roles():
    updated = 0
    async for db in get_db():
        result = await db.execute(select(Contact))
        contacts = result.scalars().all()

        for contact in contacts:
            current_role = contact.role or ""
            # Only update contacts that have a vague/missing role
            if current_role.strip() in {"General", "General Contact", "Unknown", ""}:
                new_role = infer_role_from_email(contact.email)
                if new_role != current_role:
                    print(f"  {contact.email:45s}  '{current_role}' -> '{new_role}'")
                    contact.role = new_role
                    updated += 1

        await db.commit()
        print(f"\nBackfill complete. Updated {updated} contacts.")

if __name__ == "__main__":
    asyncio.run(backfill_roles())
