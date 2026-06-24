import asyncio
import datetime
from sqlalchemy import select
from core.database import get_db
from core.models import Company, Contact, EmailStatus
from services.enrichment import find_contacts
from services.verification import verify_email

async def enrich_companies():
    print("Starting Enrichment Engine...")
    async for db in get_db():
        result = await db.execute(select(Company))
        companies = result.scalars().all()
        
        processed = 0
        for company in companies:
            # Check if company already has contacts
            contact_check = await db.execute(select(Contact).where(Contact.company_id == company.id))
            existing_contacts = contact_check.scalars().all()
            
            if existing_contacts:
                print(f"Skipping {company.domain} (already enriched)")
                continue
                
            print(f"Enriching {company.domain}...")
            emails_data = await find_contacts(company.domain)
            
            if not emails_data:
                print(f"  No contacts found for {company.domain}")
                continue
                
            for e_data in emails_data:
                # Support both Hunter's actual 'value' format and our mock 'value'/'email' fallback
                email_addr = e_data.get('email') or e_data.get('value')
                first_name = e_data.get('first_name') or ''
                last_name = e_data.get('last_name') or ''
                name = f"{first_name} {last_name}".strip()
                position = e_data.get('position')
                linkedin = e_data.get('linkedin')
                
                if not email_addr:
                    continue
                    
                # Check if email exists
                email_check = await db.execute(select(Contact).where(Contact.email == email_addr))
                if email_check.scalars().first():
                    continue

                # Create contact
                contact = Contact(
                    company_id=company.id,
                    name=name,
                    email=email_addr,
                    role=position,
                    linkedin_url=linkedin
                )
                db.add(contact)
                await db.flush() # flush to generate the contact.id needed for EmailStatus
                
                # Verify email
                verif_result = await verify_email(email_addr)
                
                # Create email status
                status = EmailStatus(
                    contact_id=contact.id,
                    status=verif_result.get('status', 'unknown'),
                    bounce_reason=verif_result.get('sub_status', ''),
                    checked_at=datetime.datetime.utcnow()
                )
                db.add(status)
                
                print(f"  Added {name} ({email_addr}) - Status: {status.status}")
                
            await db.commit()
            processed += 1
            
        print(f"Enrichment complete. Processed {processed} new companies.")

if __name__ == "__main__":
    asyncio.run(enrich_companies())
