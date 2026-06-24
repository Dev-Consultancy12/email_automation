import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    industry = Column(String(100))
    headcount = Column(String(50))
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("Contact", back_populates="company")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    name = Column(String(255))
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(100))
    linkedin_url = Column(Text)
    opted_out = Column(Boolean, default=False)

    company = relationship("Company", back_populates="contacts")
    email_status = relationship("EmailStatus", back_populates="contact", uselist=False)
    scheduled_sends = relationship("ScheduledSend", back_populates="contact")
    outreach_logs = relationship("OutreachLog", back_populates="contact")

class EmailStatus(Base):
    __tablename__ = "email_status"

    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), primary_key=True)
    status = Column(String(50))
    checked_at = Column(DateTime)
    bounce_reason = Column(Text)

    contact = relationship("Contact", back_populates="email_status")

class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    subject = Column(String(255))
    body_html = Column(Text)
    body_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    scheduled_sends = relationship("ScheduledSend", back_populates="template")
    outreach_logs = relationship("OutreachLog", back_populates="template")

class ScheduledSend(Base):
    __tablename__ = "scheduled_sends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"))
    scheduled_for = Column(DateTime)
    status = Column(String(50))

    contact = relationship("Contact", back_populates="scheduled_sends")
    template = relationship("Template", back_populates="scheduled_sends")

class OutreachLog(Base):
    __tablename__ = "outreach_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"))
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    replied_at = Column(DateTime)

    contact = relationship("Contact", back_populates="outreach_logs")
    template = relationship("Template", back_populates="outreach_logs")
