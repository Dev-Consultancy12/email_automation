import asyncio
from sqlalchemy import select
from core.database import get_db
from core.models import Contact

async def show_contacts():
    async for db in get_db():
        result = await db.execute(select(Contact))
        contacts = result.scalars().all()
        for c in contacts:
            print(f"- **{c.name}** ({c.role}) - {c.email}")
        break

if __name__ == "__main__":
    asyncio.run(show_contacts())
