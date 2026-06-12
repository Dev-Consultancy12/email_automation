from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from api.webhooks import router as webhooks_router
from sqlalchemy import select
from core.database import get_db
from core.models import Contact, Company

app = FastAPI(title="Antigravity Engine API")

app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/", response_class=HTMLResponse)
async def read_root(db=Depends(get_db)):
    result_companies = await db.execute(select(Company))
    companies = result_companies.scalars().all()
    
    result_contacts = await db.execute(select(Contact))
    contacts = result_contacts.scalars().all()

    html = f"""
    <html>
        <head>
            <title>Antigravity Dashboard</title>
            <style>
                body {{ font-family: system-ui, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }}
                h1 {{ color: #38bdf8; }}
                h2 {{ color: #94a3b8; margin-top: 40px; }}
                table {{ border-collapse: collapse; width: 100%; background: #1e293b; margin-bottom: 30px; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
                th, td {{ text-align: left; padding: 12px 16px; border-bottom: 1px solid #334155; }}
                th {{ background-color: #0f172a; font-weight: 600; color: #cbd5e1; }}
                td {{ color: #f1f5f9; }}
                tr:last-child td {{ border-bottom: none; }}
            </style>
        </head>
        <body>
            <h1>🚀 Antigravity Engine Live Output</h1>
            
            <h2>🏢 Scraped Companies ({len(companies)})</h2>
            <table>
                <tr><th>Name</th><th>Domain</th><th>Source</th></tr>
                {''.join(f"<tr><td>{c.name}</td><td>{c.domain}</td><td>{c.source}</td></tr>" for c in companies)}
            </table>
            
            <h2>👤 Enriched Contacts ({len(contacts)})</h2>
            <table>
                <tr><th>Name</th><th>Role</th><th>Email</th></tr>
                {''.join(f"<tr><td>{c.name}</td><td>{c.role}</td><td>{c.email}</td></tr>" for c in contacts)}
            </table>
        </body>
    </html>
    """
    return html
