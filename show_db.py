import asyncio
from sqlalchemy import select
from core.database import get_db
from core.models import Company

async def show_data():
    async for db in get_db():
        result = await db.execute(select(Company))
        companies = result.scalars().all()
        for c in companies:
            print(f"- **{c.name}** ({c.domain}) - Source: {c.source}")
        break

if __name__ == "__main__":
    asyncio.run(show_data())
