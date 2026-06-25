from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from api.webhooks import router as webhooks_router
from sqlalchemy import select

from sqlalchemy.orm import selectinload
from core.database import get_db
from core.models import Contact, Company, EmailStatus

from core.database import get_db
from core.models import Contact, Company


app = FastAPI(title="Antigravity Engine API")

app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/", response_class=HTMLResponse)
async def read_root(db=Depends(get_db)):
    result_companies = await db.execute(select(Company))
    companies = result_companies.scalars().all()


    # Eager-load email_status for each contact
    result_contacts = await db.execute(
        select(Contact).options(selectinload(Contact.email_status), selectinload(Contact.company))
    )
    contacts = result_contacts.scalars().all()

    # Stats
    total_contacts = len(contacts)
    valid_count = sum(1 for c in contacts if c.email_status and c.email_status.status == "valid")
    invalid_count = sum(1 for c in contacts if c.email_status and c.email_status.status == "invalid")
    unknown_count = total_contacts - valid_count - invalid_count

    def status_badge(contact):
        if not contact.email_status:
            return '<span style="color:#64748b">—</span>'
        s = contact.email_status.status
        colors = {"valid": "#22c55e", "invalid": "#ef4444", "unknown": "#f59e0b"}
        color = colors.get(s, "#94a3b8")
        return f'<span style="color:{color};font-weight:600">{s}</span>'

    def company_name(contact):
        return contact.company.name if contact.company else "—"

    contact_rows = "".join(
        f"<tr><td>{c.name or '—'}</td><td>{company_name(c)}</td><td>{c.role or '—'}</td>"
        f"<td>{c.email}</td><td>{status_badge(c)}</td></tr>"
        for c in contacts
    )

    company_rows = "".join(
        f"<tr><td>{c.name}</td><td>{c.domain}</td><td>{c.source}</td></tr>"
        for c in companies
    )


    
    result_contacts = await db.execute(select(Contact))
    contacts = result_contacts.scalars().all()


    html = f"""
    <html>
        <head>
            <title>Antigravity Dashboard</title>
            <style>
                body {{ font-family: system-ui, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }}

                h1 {{ color: #38bdf8; margin-bottom: 4px; }}
                h2 {{ color: #94a3b8; margin-top: 40px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0 10px; }}
                .stat-card {{ background: #1e293b; border-radius: 8px; padding: 16px 24px; min-width: 120px; text-align: center; border: 1px solid #334155; }}
                .stat-card .num {{ font-size: 2rem; font-weight: 700; }}
                .stat-card .label {{ font-size: 0.8rem; color: #94a3b8; margin-top: 2px; }}
                table {{ border-collapse: collapse; width: 100%; background: #1e293b; margin-bottom: 30px; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
                th, td {{ text-align: left; padding: 12px 16px; border-bottom: 1px solid #334155; }}
                th {{ background-color: #0f172a; font-weight: 600; color: #cbd5e1; }}
                td {{ color: #f1f5f9; font-size: 0.93rem; }}
                tr:last-child td {{ border-bottom: none; }}
                tr:hover td {{ background: #1a2844; }}

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

            <p style="color:#64748b;margin-top:0">Real-time view of scraped companies and enriched contacts</p>

            <div class="stats">
                <div class="stat-card"><div class="num" style="color:#38bdf8">{len(companies)}</div><div class="label">Companies</div></div>
                <div class="stat-card"><div class="num" style="color:#a78bfa">{total_contacts}</div><div class="label">Contacts</div></div>
                <div class="stat-card"><div class="num" style="color:#22c55e">{valid_count}</div><div class="label">Valid Emails</div></div>
                <div class="stat-card"><div class="num" style="color:#ef4444">{invalid_count}</div><div class="label">Invalid</div></div>
                <div class="stat-card"><div class="num" style="color:#f59e0b">{unknown_count}</div><div class="label">Unknown</div></div>
            </div>

            <h2>🏢 Scraped Companies ({len(companies)})</h2>
            <table>
                <tr><th>Name</th><th>Domain</th><th>Source</th></tr>
                {company_rows}
            </table>

            <h2>👤 Enriched Contacts ({total_contacts})</h2>
            <table>
                <tr><th>Name</th><th>Company</th><th>Role</th><th>Email</th><th>Status</th></tr>
                {contact_rows}

            
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




