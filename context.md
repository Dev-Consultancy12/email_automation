# Project Antigravity: Master Context

## 1. Project Overview
**Antigravity** is an automated B2B lead generation and cold-outreach engine designed for a consultancy software services company. It automatically discovers product-based startups, extracts and enriches decision-maker contact details, verifies email deliverability, and schedules personalized cold outreach sequences.

**Core Philosophy:** 
- Protect sending domain reputation at all costs.
- Never send an unverified email.
- Treat the PostgreSQL database as the single source of truth.
- Decouple scraping, processing, and sending via asynchronous task queues.

---

## 2. Tech Stack Definition
- **Language:** Python 3.11+
- **Database:** PostgreSQL (hosted via Supabase/RDS)
- **ORM:** SQLAlchemy or SQLModel
- **API/Dashboard Backend:** FastAPI (Fast, async-native, auto-docs)
- **Scraping Layer:** Playwright (for JS-heavy sites) & Scrapy (for static/bulk directories)
- **Task Queue & Workers:** Celery + Redis (Message Broker) OR APScheduler (for V1 MVP)
- **External Integrations:**
  - *Enrichment:* Hunter.io API
  - *Verification:* ZeroBounce API
  - *Sending:* SendGrid API (with Webhooks for event tracking)

---

## 3. System Architecture (The 6 Stages)
1. **Discover:** Cron-scheduled workers scrape Product Hunt, YC Directory, and Crunchbase to find target companies.
2. **Scrape:** Playwright/Scrapy visits the target companies' domains to extract raw contact info, social links, and metadata.
3. **Enrich & Verify:** 
   - Pass domains to Hunter.io to find missing emails.
   - Pass all emails to ZeroBounce. Only emails marked `valid` move forward.
4. **Store:** All state changes are written to the PostgreSQL database.
5. **Schedule:** A worker runs daily, checking the `scheduled_sends` table to batch emails into the queue based on strict rate limits (max 50/day) and time windows (Tue-Thu, 9am-11am).
6. **Send & Track:** SendGrid executes the email. A FastAPI webhook endpoint listens for `delivered`, `opened`, `clicked`, `replied`, and `bounced` events to update the DB and halt future sequence steps if necessary.

---

## 4. Database Schema (PostgreSQL)

```sql
-- Core Tables Representation

CREATE TABLE companies (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    industry VARCHAR(100),
    headcount VARCHAR(50),
    source VARCHAR(100), -- e.g., 'product_hunt', 'yc_directory'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(100),
    linkedin_url TEXT,
    opted_out BOOLEAN DEFAULT FALSE
);

CREATE TABLE email_status (
    contact_id UUID REFERENCES contacts(id) PRIMARY KEY,
    status VARCHAR(50), -- 'valid', 'risky', 'invalid', 'spamtrap'
    checked_at TIMESTAMP,
    bounce_reason TEXT
);

CREATE TABLE templates (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    subject VARCHAR(255),
    body_html TEXT,
    body_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scheduled_sends (
    id UUID PRIMARY KEY,
    contact_id UUID REFERENCES contacts(id),
    template_id UUID REFERENCES templates(id),
    scheduled_for TIMESTAMP,
    status VARCHAR(50) -- 'pending', 'sent', 'skipped', 'failed'
);

CREATE TABLE outreach_log (
    id UUID PRIMARY KEY,
    contact_id UUID REFERENCES contacts(id),
    template_id UUID REFERENCES templates(id),
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    replied_at TIMESTAMP
);
```

---

## 5. Proposed Directory Structure

```text
antigravity/
│
├── api/                    # FastAPI application (Endpoints & Webhooks)
│   ├── main.py
│   ├── routes/
│   │   ├── campaigns.py
│   │   ├── webhooks.py     # SendGrid event listener
│   └── schemas.py          # Pydantic models for API
│
├── core/                   # Shared business logic and config
│   ├── config.py           # Env var loading
│   ├── database.py         # DB connection & session management
│   └── models.py           # SQLAlchemy ORM models
│
├── scrapers/               # Stage 1 & 2 logic
│   ├── spiders/            # Scrapy/Playwright scripts
│   └── extractors.py       # HTML parsing logic
│
├── services/               # Stage 3 & 6 external integrations
│   ├── hunter_client.py    # Hunter.io API logic
│   ├── zerobounce.py       # Verification logic
│   └── sendgrid_client.py  # Email dispatch
│
├── workers/                # Stage 5 Async tasks (Celery/APScheduler)
│   ├── celery_app.py
│   ├── discovery_tasks.py  # Cron jobs for scraping
│   ├── enrich_tasks.py     # Async enrichment/verification
│   └── sender_tasks.py     # Outreach queue processor
│
├── pyproject.toml          # Dependencies
├── .env.example            # Environment variables template
└── docker-compose.yml      # Local Redis/Postgres setup
```

---

## 6. Environment Variables (`.env`)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/antigravity

# Task Queue (If using Celery)
REDIS_URL=redis://localhost:6379/0

# External APIs
HUNTER_API_KEY=your_hunter_key
ZEROBOUNCE_API_KEY=your_zerobounce_key
SENDGRID_API_KEY=your_sendgrid_key

# Webhook Security
SENDGRID_WEBHOOK_SECRET=your_webhook_signing_secret

# Application Settings
ENVIRONMENT=development # or production
MAX_EMAILS_PER_DAY=50
```

---

## 7. Implementation Roadmap

* **Phase 1: Foundation.** Setup PostgreSQL schema, SQLAlchemy models, and basic CRUD.
* **Phase 2: Ingestion Pipeline.** Build the `scrapers/` module for Product Hunt and YC. Save raw data to the `companies` and `contacts` tables.
* **Phase 3: Enrichment & Verification.** Implement the `services/` layer to call Hunter.io and ZeroBounce. Update the `email_status` table.
* **Phase 4: Scheduling & Sending.** Setup the worker queue to read `scheduled_sends` and dispatch via SendGrid.
* **Phase 5: The Feedback Loop.** Build the FastAPI webhook endpoint to listen to SendGrid events and update `outreach_log`.

---

## 8. Core Rules & Constraints

1. **Rate Limiting:** Scrapers must use random delays (1-3 seconds) between page requests and respect `robots.txt`.
2. **Idempotency:** Task workers must be idempotent. If a scraping or sending task fails and retries, it must not create duplicate DB records or send a duplicate email.
3. **Data Integrity:** A contact cannot be queued for sending unless `email_status.status == 'valid'`.
4. **Legal Compliance:** Every email template MUST include a one-click unsubscribe link. If a webhook registers an unsubscribe, `contacts.opted_out` must immediately flip to `TRUE`.
